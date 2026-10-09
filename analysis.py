"""SaaS subscription analytics: synthetic data -> SQL (SQLite) -> Pandas -> Tableau-ready CSVs."""
import sqlite3, json, random
import pandas as pd, numpy as np
random.seed(7); np.random.seed(7)

CH = {'Organic':(0.16,0), 'Referral':(0.22,6), 'Email':(0.13,4), 'Paid Search':(0.09,38), 'Social':(0.06,30)}
PLANS = {'Basic':29,'Pro':79,'Enterprise':249}
REG = ['North America','Europe','Asia-Pacific','Latin America']
months = pd.period_range('2024-01','2025-12',freq='M')

leads, cust = [], []
lid = cid = 0
for p in months:
    for ch,(cr,_) in CH.items():
        n = int(np.random.normal(60 if ch in('Organic','Paid Search') else 35, 6)*(1+0.03*(p.ordinal-months[0].ordinal)))
        for _ in range(n):
            lid += 1
            d = p.start_time + pd.Timedelta(days=int(np.random.randint(0,p.days_in_month)))
            conv = int(np.random.rand() < cr)
            leads.append((lid,d.date().isoformat(),ch,conv))
            if conv:
                cid += 1
                plan = np.random.choice(list(PLANS),p=[.55,.35,.10])
                sd = d + pd.Timedelta(days=int(np.random.randint(1,15)))
                churn_p = {'Basic':.045,'Pro':.028,'Enterprise':.015}[plan] + (0.02 if ch in('Paid Search','Social') else 0)
                life = np.random.geometric(churn_p)
                cd = sd + pd.DateOffset(months=int(life))
                cd = cd.date().isoformat() if cd <= pd.Timestamp('2025-12-31') else None
                cust.append((cid,lid,sd.date().isoformat(),plan,np.random.choice(REG),PLANS[plan],cd))
BUD={'Organic':0,'Referral':900,'Email':500,'Paid Search':3200,'Social':1800}
spend=[(str(p),ch,round(max(np.random.normal(BUD[ch],BUD[ch]*0.12),0),2)) for p in months for ch in CH]

leads_df = pd.DataFrame(leads,columns=['lead_id','created_date','channel','converted'])
cust_df = pd.DataFrame(cust,columns=['customer_id','lead_id','signup_date','plan','region','monthly_price','churn_date'])
spend_df = pd.DataFrame(spend,columns=['month','channel','spend'])
mon_df = pd.DataFrame({'month':[str(p) for p in months],'month_end':[p.end_time.date().isoformat() for p in months]})
mon_df['month'] = mon_df['month']+'-01'
spend_df['month'] = spend_df['month']+'-01'

con = sqlite3.connect(':memory:')
for n,df in [('leads',leads_df),('customers',cust_df),('marketing_spend',spend_df),('months',mon_df)]:
    df.to_sql(n,con,index=False); df.to_csv(f'data/{n}.csv',index=False)

q = open('queries.sql').read().split(';')
q = [x.strip() for x in q if 'SELECT' in x]
names = ['mrr','mrr_growth','churn','conversion','cac']
res = {n:pd.read_sql(s,con) for n,s in zip(names,q)}
res['churn']['churn_pct'] = (100*res['churn'].churned/res['churn'].start_customers.replace(0,np.nan)).round(2)
for n,df in res.items(): df.to_csv(f'data/result_{n}.csv',index=False)

# Python analysis: outliers (z-score on churn) and correlation
c = res['churn'].dropna(); c = c[c.start_customers>=100]; z = (c.churn_pct-c.churn_pct.mean())/c.churn_pct.std()
anom = c[z.abs()>1.8][['month','churn_pct']]
plan_mix = cust_df.groupby('plan').monthly_price.agg(['count','sum']).reset_index()
json.dump({k:v.to_dict('records') for k,v in res.items()}|{'anomalies':anom.to_dict('records'),'plan_mix':plan_mix.to_dict('records')},open('data/results.json','w'))
print({k:v.tail(3).to_dict('records') if k in('mrr','churn') else v.to_dict('records') for k,v in res.items()})
print('anomalies',anom.to_dict('records')); print(len(leads_df),len(cust_df))
