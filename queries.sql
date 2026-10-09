-- 1. Monthly MRR, active customers (CTE + join to months table)
WITH active AS (
  SELECT m.month, c.customer_id, c.monthly_price
  FROM months m JOIN customers c
    ON c.signup_date <= m.month_end AND (c.churn_date IS NULL OR c.churn_date > m.month_end))
SELECT month, COUNT(customer_id) AS active_customers, SUM(monthly_price) AS mrr
FROM active GROUP BY month ORDER BY month;

-- 2. MoM MRR growth (window function LAG)
WITH mrr AS (
  SELECT m.month, SUM(c.monthly_price) AS mrr
  FROM months m JOIN customers c
    ON c.signup_date <= m.month_end AND (c.churn_date IS NULL OR c.churn_date > m.month_end)
  GROUP BY m.month)
SELECT month, mrr, ROUND(100.0*(mrr - LAG(mrr) OVER (ORDER BY month))/LAG(mrr) OVER (ORDER BY month),2) AS mom_growth_pct
FROM mrr;

-- 3. Monthly churn rate (subquery)
SELECT m.month,
  (SELECT COUNT(*) FROM customers c WHERE c.signup_date < m.month AND (c.churn_date IS NULL OR c.churn_date >= m.month)) AS start_customers,
  (SELECT COUNT(*) FROM customers c WHERE c.churn_date BETWEEN m.month AND m.month_end) AS churned
FROM months m ORDER BY m.month;

-- 4. Conversion rate by channel
SELECT channel, COUNT(*) AS leads, SUM(converted) AS customers, ROUND(100.0*SUM(converted)/COUNT(*),2) AS conversion_pct
FROM leads GROUP BY channel ORDER BY conversion_pct DESC;

-- 5. CAC by channel (pre-aggregated subqueries avoid join fan-out)
SELECT s.channel, ROUND(s.spend,0) AS total_spend, n.new_customers,
       ROUND(s.spend*1.0/NULLIF(n.new_customers,0),2) AS cac
FROM (SELECT channel, SUM(spend) AS spend FROM marketing_spend GROUP BY channel) s
JOIN (SELECT l.channel, COUNT(*) AS new_customers FROM leads l
      JOIN customers c ON c.lead_id = l.lead_id GROUP BY l.channel) n ON n.channel = s.channel
ORDER BY cac;
