from drf_spectacular.utils import extend_schema_view, extend_schema

from accounts.serialisers import AccountSerializer, AccountSerializerDetail, AccountPutSerializer, \
    AccountPatchSerializer

listAccountSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список всех счетов текущего пользователя. "
        "Каждый аккаунт связан с пользователем и содержит "
        "информацию о балансе.",
        responses={
            200: AccountSerializer(),
        },
    ),
    post=extend_schema(
        description="Создать новый счет для текущего пользователя. "
        "Укажите название счета и начальный баланс.",
        request=AccountSerializer,
        responses={
            201: AccountSerializer,
        },
    ),
)


RetrieveUpdateDeleteAccountSchema = extend_schema_view(
    get=extend_schema(
        description="Получить детальную информацию о счете. В счет добавляется информация о "
        "последних доходах и расходах за последние 30 дней.",
        responses={
            200: AccountSerializerDetail(many=True),
        },
    ),
    put=extend_schema(
        description="Обновить все данные о счете(название и баланс)",
        request=AccountPutSerializer,
        responses={
            200: AccountSerializer,
        },
    ),
    patch=extend_schema(
        description="Изменить баланс счета.",
        request=AccountPatchSerializer,
        responses={
            200: AccountSerializer,
        },
    ),
    delete=extend_schema(description="Удалить счет."),
)
