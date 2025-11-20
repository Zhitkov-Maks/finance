async def generate_detail_analytics(
    data: dict, type_analytics
) -> str:
    period = data["month_name"] + f" {data['period'][:4]} года."
    if 'exp' in type_analytics:
        message = f"Аналитика расходов за {period}\n\n"
        sign = "потрачено"
    else:
        message = f"Aналитика доходов за {period}\n\n"
        sign = "заработано"

    message += (
        f"Всего {sign}: {float(data["total_amount"]):,.1f}₱.\n"
        f"Количество операций: {data['transaction_count']}.\n"
        f"Средняя величина транзакции: {float(data['avg_amount']):,.1f}₱.\n"
    )

    if not data.get("is_first_month"):
        message += (
            f"В сравнении с певым месяцем в году: \n"
            f"....{float(data['absolute_change_vs_first']):+,.1f}₱.\n"
            f"....{float(data['change_vs_first_percent']):+,.0f}%.\n"
            f"....Тренд: {data["trend_vs_first"]}.\n"
            
            f"В сравнении с предыдущим месяцем: \n"
            f"....{float(data['absolute_change_vs_prev']):+,.1f}₱.\n"
            f"....{float(data['change_vs_prev_percent']):+,.0f}%.\n"
            f"....Тренд: {data["trend_vs_prev"]}.\n"
        )
    return message
