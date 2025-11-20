-- Рассчет аналитики по месяцам.
WITH monthly_stats AS (
    SELECT 
        EXTRACT(YEAR FROM t.create_at) as year,
        EXTRACT(MONTH FROM t.create_at) as month,
        SUM(t.amount) as total_amount,
        COUNT(t.id) as transaction_count,
        AVG(t.amount) as avg_amount,
        FIRST_VALUE(SUM(t.amount)) OVER w as first_month_amount,
        LAG(SUM(t.amount)) OVER w as prev_month_amount
    FROM transactions t
    INNER JOIN transactions_category c ON t.category_id = c.id
    WHERE t.user_id = %s 
        AND c.type_transaction = %s
        AND (%s IS NULL OR EXTRACT(YEAR FROM t.create_at) = %s)
    GROUP BY 
        EXTRACT(YEAR FROM t.create_at),
        EXTRACT(MONTH FROM t.create_at)
    WINDOW w AS (ORDER BY EXTRACT(YEAR FROM t.create_at), EXTRACT(MONTH FROM t.create_at))
)
SELECT 
    year::integer,
    month::integer,
    total_amount,
    transaction_count,
    avg_amount,
    first_month_amount,
    prev_month_amount,
    CASE 
        WHEN first_month_amount != 0 
        THEN ROUND((total_amount - first_month_amount) / ABS(first_month_amount) * 100, 2)
        ELSE 0.0
    END as change_vs_first_percent,
    CASE 
        WHEN prev_month_amount IS NOT NULL AND prev_month_amount != 0 
        THEN ROUND((total_amount - prev_month_amount) / ABS(prev_month_amount) * 100, 2)
        ELSE NULL
    END as change_vs_prev_percent
FROM monthly_stats
ORDER BY year, month
