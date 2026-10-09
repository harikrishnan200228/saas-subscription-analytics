# SaaS Subscription Analytics: SQL -> Python -> Tableau

End-to-end analysis of 7,278 leads and 945 customers (Jan 2024 - Dec 2025, synthetic data).

**Workflow:** `analysis.py` generates data and loads SQLite -> `queries.sql` (CTEs, joins, subqueries, window functions) -> Pandas cleaning, KPIs and outlier check -> `data/*.csv` for Tableau -> executive dashboard.

**KPIs:** MRR, MoM growth, churn rate, conversion rate, CAC by channel.

**Tableau:** connect `data/result_*.csv` (or `leads.csv`, `customers.csv`) in Tableau Public and rebuild the dashboard.

Run: `python analysis.py && python build_dashboard.py`
