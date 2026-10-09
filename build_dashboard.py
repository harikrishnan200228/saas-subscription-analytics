import json
d=json.load(open('data/results.json'))
mrr=d['mrr'];ch=d['churn'];cv=d['conversion'];cac=d['cac'];pm=d['plan_mix']
last=mrr[-1]['mrr']; act=mrr[-1]['active_customers']
tot_l=sum(x['leads'] for x in cv); tot_c=sum(x['customers'] for x in cv)
spend=sum(x['total_spend'] for x in cac)
rc=[x['churn_pct'] for x in ch if x['churn_pct'] is not None][-6:]; churn6=sum(rc)/len(rc)
yoy=100*(last/mrr[11]['mrr']-1)
W,H=640,200
mx=max(x['mrr'] for x in mrr)
pts=" ".join(f"{20+i*(W-40)/(len(mrr)-1):.1f},{H-20-(x['mrr']/mx)*(H-40):.1f}" for i,x in enumerate(mrr))
line=f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="MRR trend"><polyline points="{pts}" fill="none" stroke="var(--a)" stroke-width="3"/><text x="20" y="14" fill="var(--m)" font-size="12">Jan 2024</text><text x="{W-20}" y="14" text-anchor="end" fill="var(--m)" font-size="12">Dec 2025: ${last:,.0f}</text></svg>'
cmax=max(x['conversion_pct'] for x in cv)
crow="".join(f'<div class="r"><span>{x["channel"]}</span><div class="b"><i style="width:{x["conversion_pct"]/cmax*100:.0f}%"></i></div><b>{x["conversion_pct"]:.1f}%</b></div>' for x in cv)
kmax=max(x['cac'] for x in cac)
krow="".join(f'<div class="r"><span>{x["channel"]}</span><div class="b"><i class="w" style="width:{max(x["cac"]/kmax*100,1):.0f}%"></i></div><b>${x["cac"]:,.0f}</b></div>' for x in cac)
best=cv[0]; worst=cac[-1]; ps=[x for x in cac if x['channel']=='Paid Search'][0]
anom=d['anomalies'][0]
ins=[f"{best['channel']} converts best ({best['conversion_pct']:.1f}% vs {cv[-1]['conversion_pct']:.1f}% for {cv[-1]['channel']}) at a CAC of only ${[x for x in cac if x['channel']==best['channel']][0]['cac']:,.0f}.",
f"{worst['channel']} CAC is ${worst['cac']:,.0f} per customer, about {worst['cac']/[x for x in cac if x['channel']=='Email'][0]['cac']:.0f}x Email. Recommend shifting budget from Social/Paid Search to Referral and Email.",
f"Churn averaged {churn6:.1f}% over the last 6 months. Nov 2024 spiked to {anom['churn_pct']}% (outlier, z-score above 1.8) and should be investigated.",
f"MRR grew {yoy:.0f}% year over year to ${last:,.0f}, but MoM growth slowed from double digits in 2024 to about 3-6% in late 2025."]
html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>SaaS Executive Dashboard</title>
<style>:root{{--bg:#f6f8fb;--c:#fff;--t:#14213d;--m:#667085;--a:#1f6feb;--w:#d9480f;--bd:#e3e8ef;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0f1624;--c:#182236;--t:#eef2f8;--m:#9aa8bf;--a:#5b9dff;--w:#ff8a4c;--bd:#263450}}}}
body{{margin:0;background:var(--bg);color:var(--t);font-family:system-ui,Segoe UI,Arial,sans-serif;padding:16px;max-width:900px;margin-inline:auto}}
h1{{font-size:22px;margin:4px 0}}p.s{{color:var(--m);margin:0 0 14px;font-size:13px}}
.k{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}.card{{background:var(--c);border:1px solid var(--bd);border-radius:12px;padding:12px;margin-bottom:10px}}
.k .card{{margin:0}}.k small{{color:var(--m);font-size:12px}}.k b{{display:block;font-size:22px;margin-top:2px}}h2{{font-size:15px;margin:0 0 8px}}
.r{{display:grid;grid-template-columns:90px 1fr 64px;gap:8px;align-items:center;font-size:13px;margin:6px 0}}.b{{background:var(--bd);height:10px;border-radius:5px;overflow:hidden}}.b i{{display:block;height:100%;background:var(--a)}}.b i.w{{background:var(--w)}}.r b{{text-align:right}}
svg{{width:100%;height:auto}}li{{margin:6px 0;font-size:14px;line-height:1.4}}ul{{padding-left:18px;margin:0}}@media(min-width:700px){{.k{{grid-template-columns:repeat(4,1fr)}}}}</style></head><body>
<h1>SaaS Subscription Executive Dashboard</h1><p class="s">Jan 2024 - Dec 2025 | Synthetic dataset | SQL, Python, Tableau-ready</p>
<div class="k"><div class="card"><small>MRR (Dec 2025)</small><b>${last:,.0f}</b></div><div class="card"><small>Active customers</small><b>{act}</b></div>
<div class="card"><small>Lead-to-customer conversion</small><b>{100*tot_c/tot_l:.1f}%</b></div><div class="card"><small>Avg churn (last 6 mo)</small><b>{churn6:.1f}%</b></div></div>
<div class="card" style="margin-top:10px"><h2>Monthly Recurring Revenue</h2>{line}</div>
<div class="card"><h2>Conversion rate by channel</h2>{crow}</div>
<div class="card"><h2>Customer acquisition cost (CAC) by channel</h2>{krow}</div>
<div class="card"><h2>Key insights and recommendations</h2><ul>{"".join(f"<li>{i}</li>" for i in ins)}</ul></div>
</body></html>'''
open('/mnt/user-data/outputs/saas_executive_dashboard.html','w').write(html)
print(ins)
