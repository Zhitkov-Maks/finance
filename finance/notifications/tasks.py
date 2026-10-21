import json
import logging
from datetime import date, timedelta
from decimal import Decimal

from celery import shared_task
from django.conf import settings

from .models import Notification, NotificationPreferences, PushSubscription
from .services import create_notification

logger = logging.getLogger(__name__)


# ---------- Отправка push ----------
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, notification_id: str):
    notif = (
        Notification.objects.select_related("user").filter(id=notification_id).first()
    )
    if not notif or notif.is_push_sent:
        return

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.warning("pywebpush not installed, push disabled")
        return

    payload = json.dumps(
        {
            "title": notif.title,
            "body": notif.message,
            "data": notif.data,
            "notification_id": str(notif.id),
        }
    )

    dead_ids = []
    sent_ok = False

    for sub in PushSubscription.objects.filter(user=notif.user):
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"},
            )
            sent_ok = True
        except WebPushException as exc:
            status = exc.response.status_code if exc.response else None
            logger.warning("Push failed sub=%s status=%s", sub.id, status)
            if status in (404, 410):
                dead_ids.append(sub.id)

    if dead_ids:
        PushSubscription.objects.filter(id__in=dead_ids).delete()

    if sent_ok:
        Notification.objects.filter(id=notif.id).update(is_push_sent=True)


# ---------- Платежи ----------
@shared_task
def check_upcoming_payments():
    """
    Раз в день:
      - за N дней до next_run_date   -> payment_upcoming
      - если next_run_date = сегодня -> payment_today
    """
    from recurring.models import RecurringTransaction

    today = date.today()
    created = 0

    user_ids = (
        RecurringTransaction.objects.filter(is_active=True)
        .values_list("user_id", flat=True)
        .distinct()
    )

    for uid in user_ids:
        prefs = NotificationPreferences.objects.filter(user_id=uid).first()
        if not prefs or not prefs.payment_alerts:
            continue
        target = today + timedelta(days=prefs.payment_days_before or 1)

        created += _notify_recurring_batch(
            uid,
            target,
            Notification.TYPE_PAYMENT_UPCOMING,
            title_prefix="Скоро платёж",
            verb="спишется",
        )
        created += _notify_recurring_batch(
            uid,
            today,
            Notification.TYPE_PAYMENT_TODAY,
            title_prefix="Сегодня платёж",
            verb="списывается сегодня",
        )

    return f"Payment notifications: {created}"


def _notify_recurring_batch(user_id, target_date, ntype, title_prefix, verb):
    from recurring.models import RecurringTransaction

    created = 0
    for rec in RecurringTransaction.objects.filter(
        user_id=user_id, is_active=True, next_run_date=target_date
    ).select_related("category", "account"):
        exists = Notification.objects.filter(
            user_id=user_id,
            notification_type=ntype,
            data__recurring_id=rec.id,
            data__for_date=str(target_date),
        ).exists()
        if exists:
            continue
        create_notification(
            user=rec.user,
            notification_type=ntype,
            title=f"{title_prefix}: {rec.title}",
            message=f"{rec.title} — {rec.amount} ₽ {verb} {target_date:%d.%m.%Y}.",
            data={
                "recurring_id": rec.id,
                "for_date": str(target_date),
                "amount": str(rec.amount),
            },
        )
        created += 1
    return created


# ---------- Бюджеты ----------
@shared_task
def check_budgets_for_user(user_id: int):
    from budgets.models import Budget
    from budgets.services import compute_budget_summary
    from django.contrib.auth import get_user_model

    prefs = NotificationPreferences.objects.filter(user_id=user_id).first()
    if not prefs or not prefs.budget_alerts:
        return 0

    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        return 0

    today = date.today()
    created = 0

    for period_type, _ in Budget.PERIOD_CHOICES:
        summary = compute_budget_summary(user, period_type, today)
        if not summary:
            continue
        period_key = f"{summary['period']['start']}_{summary['period']['end']}"

        if summary.get("total_budget"):
            tb = summary["total_budget"]
            created += _maybe_notify_budget(
                user,
                tb["id"],
                "Общий бюджет",
                Decimal(str(tb["amount"])),
                Decimal(str(tb["spent"])),
                period_key,
                prefs,
            )
        for b in summary.get("budgets", []):
            created += _maybe_notify_budget(
                user,
                b["id"],
                f"Бюджет «{b['category']['name']}»",
                Decimal(str(b["amount"])),
                Decimal(str(b["spent"])),
                period_key,
                prefs,
            )

    return created


def _maybe_notify_budget(user, budget_id, label, amount, spent, period_key, prefs):
    if amount <= 0:
        return 0
    percent = float(spent / amount * 100)
    threshold = prefs.budget_warning_threshold or 80

    if spent > amount:
        ntype = Notification.TYPE_BUDGET_EXCEEDED
        title = f"{label}: превышен"
        message = f"{label}: потрачено {spent} ₽ из {amount} ₽ ({percent:.0f}%)."
    elif percent >= threshold:
        ntype = Notification.TYPE_BUDGET_WARNING
        title = f"{label}: почти исчерпан"
        message = f"{label}: потрачено {spent} ₽ из {amount} ₽ ({percent:.0f}%)."
    else:
        return 0

    if Notification.objects.filter(
        user=user,
        notification_type=ntype,
        data__budget_id=budget_id,
        data__period_key=period_key,
    ).exists():
        return 0

    create_notification(
        user=user,
        notification_type=ntype,
        title=title,
        message=message,
        data={
            "budget_id": budget_id,
            "period_key": period_key,
            "amount": str(amount),
            "spent": str(spent),
            "percent": round(percent, 1),
        },
    )
    return 1


@shared_task
def check_all_budgets():
    from django.contrib.auth import get_user_model

    total = 0
    for uid in (
        get_user_model().objects.filter(is_active=True).values_list("id", flat=True)
    ):
        try:
            total += check_budgets_for_user(uid) or 0
        except Exception:
            logger.exception("Budget check failed for user %s", uid)
    return f"Budget notifications: {total}"
