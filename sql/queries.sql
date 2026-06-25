SELECT amfi_code, SUM(aum) AS total_aum
FROM fact_aum
GROUP BY amfi_code
ORDER BY total_aum DESC
LIMIT 5;

SELECT
    strftime('%Y-%m', date) AS month,
    AVG(nav) AS average_nav
FROM fact_nav
GROUP BY month
ORDER BY month;

SELECT
    strftime('%Y', date) AS year,
    SUM(amount) AS total_sip
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY year
ORDER BY year;

SELECT
    im.state,
    COUNT(ft.transaction_id) AS total_transactions
FROM fact_transactions ft
JOIN investor_master im
ON ft.investor_id = im.investor_id
GROUP BY im.state
ORDER BY total_transactions DESC;

SELECT
    amfi_code,
    expense_ratio
FROM fact_performance
WHERE expense_ratio < 1;

SELECT *
FROM fact_nav
ORDER BY nav DESC
LIMIT 1;

SELECT *
FROM fact_nav
ORDER BY nav ASC
LIMIT 1;
SELECT
    transaction_type,
    SUM(amount) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

SELECT
    AVG(expense_ratio) AS average_expense_ratio
FROM fact_performance;

SELECT
    COUNT(*) AS total_funds
FROM dim_fund;