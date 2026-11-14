-- Статистика трат по дням за конкретный месяц
SELECT
    EXTRACT(DAY FROM t.create_at)::integer as day,
    SUM(t.amount) as total_amount,
    COUNT(t.id) as transaction_count
FROM transactions t
INNER JOIN transactions_category c ON t.category_id = c.id
WHERE t.user_id = %s
    AND c.type_transaction = %s
    AND EXTRACT(YEAR FROM t.create_at) = %s
    AND EXTRACT(MONTH FROM t.create_at) = %s
GROUP BY EXTRACT(DAY FROM t.create_at)
ORDER BY day;