#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300

# Figures will be written next to the manuscript for direct inclusion
output_dir = os.path.join(os.path.dirname(__file__), "..", "manuscript")
os.makedirs(output_dir, exist_ok=True)

base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
mortality_df = pd.read_csv(os.path.join(base_dir, "mortality_rates_by_administration.csv"))
deaths_df = pd.read_csv(os.path.join(base_dir, "complete_death_records.csv"))
adp_df = pd.read_csv(os.path.join(base_dir, "average_daily_population.csv"))
details_df = pd.read_csv(os.path.join(base_dir, "all_250_deaths_detailed.csv"))

# Figure 1
fig, ax = plt.subplots(figsize=(8, 6))
admins = mortality_df["administration"].values
rates = mortality_df["rate_per_100k"].values
ci_lower = mortality_df["ci_lower"].values
ci_upper = mortality_df["ci_upper"].values
yerr_lower = rates - ci_lower
yerr_upper = ci_upper - rates
x_pos = np.arange(len(admins))
ax.bar(x_pos, rates, color="steelblue", alpha=0.8, edgecolor="black", linewidth=0.5)
ax.errorbar(x_pos, rates, yerr=[yerr_lower, yerr_upper], fmt="none", ecolor="black", capsize=5, capthick=1.5, linewidth=1.5)
ax.set_xlabel("Administration", fontsize=12, fontweight="bold", labelpad=10)
ax.set_ylabel("Mortality Rate (per 100,000 person-years)", fontsize=12, fontweight="bold")
ax.set_xticks(x_pos)
ax.set_xticklabels(admins, fontsize=11)
ax.set_ylim(0, max(ci_upper) * 1.1)
ax.yaxis.grid(True, linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "Figure1.png"), dpi=300, bbox_inches="tight")
plt.close()

# Figure 2 (multi-panel):
#  - Panel A: Stacked bars by COVID vs non-COVID per fiscal year
#  - Panel B: Lines with and without COVID per fiscal year
# Build per-FY counts by cause group using detailed causes
details_df['Date_of_Death'] = pd.to_datetime(details_df['Date_of_Death'])
details_df['fiscal_year'] = details_df['Date_of_Death'].apply(lambda d: d.year if d.month < 10 else d.year+0)  # ICE FY starts Oct 1; for Oct-Dec, fiscal_year==calendar year? Adjust below
# Proper fiscal year: if month>=10 then FY = year+1
details_df['fiscal_year'] = details_df['Date_of_Death'].apply(lambda d: d.year + 1 if d.month >= 10 else d.year)
details_df['is_covid'] = details_df['Cause_of_Death'].fillna("").str.contains("covid", case=False)

fy_rows = []
for fy in sorted(details_df['fiscal_year'].unique()):
    adp_row = adp_df[adp_df['fiscal_year'] == fy]
    if len(adp_row) == 0:
        continue
    adp = adp_row['adp'].values[0]
    total = (details_df['fiscal_year'] == fy).sum()
    covid = ((details_df['fiscal_year'] == fy) & (details_df['is_covid'])).sum()
    noncovid = total - covid
    rate_covid = (covid / adp) * 100000
    rate_noncovid = (noncovid / adp) * 100000
    fy_rows.append({
        'fiscal_year': fy,
        'rate_covid': rate_covid,
        'rate_noncovid': rate_noncovid,
        'administration': adp_row['administration'].values[0]
    })
fy_stack = pd.DataFrame(fy_rows).sort_values('fiscal_year')

fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6), sharey=False)
# Panel A: stacked bars
x = np.arange(len(fy_stack))
axA.bar(x, fy_stack['rate_noncovid'], label='Non–COVID-19', color='#1f77b4', alpha=0.85)
axA.bar(x, fy_stack['rate_covid'], bottom=fy_stack['rate_noncovid'], label='COVID-19', color='#d62728', alpha=0.85)
axA.set_xticks(x)
axA.set_xticklabels(fy_stack['fiscal_year'].astype(int), rotation=45)
axA.set_ylabel('Mortality Rate (per 100,000 person-years)', fontsize=12, fontweight='bold')
axA.set_xlabel('Fiscal Year', fontsize=12, fontweight='bold')
axA.set_title('A. COVID vs non-COVID stack', fontsize=12)
axA.legend(frameon=True, fontsize=9)
axA.grid(True, linestyle='--', alpha=0.3)
axA.set_axisbelow(True)
# Panel B: with/without COVID lines
total_rate = fy_stack['rate_covid'] + fy_stack['rate_noncovid']
axB.plot(fy_stack['fiscal_year'], total_rate, 'o-', color='black', label='With COVID-19')
axB.plot(fy_stack['fiscal_year'], fy_stack['rate_noncovid'], 'o--', color='gray', label='Without COVID-19')
axB.set_xlabel('Fiscal Year', fontsize=12, fontweight='bold')
axB.set_ylabel('Mortality Rate (per 100,000 person-years)', fontsize=12, fontweight='bold')
axB.set_title('B. With vs without COVID-19', fontsize=12)
axB.legend(frameon=True, fontsize=9)
axB.grid(True, linestyle='--', alpha=0.3)
axB.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'Figure2.png'), dpi=300, bbox_inches='tight')
plt.close()

# Figure 3: Cumulative deaths by days into administration
admin_start = {
    'Bush': datetime(2001, 1, 20),
    'Obama': datetime(2009, 1, 20),
    'Trump 1': datetime(2017, 1, 20),
    'Biden': datetime(2021, 1, 20),
    'Trump 2': datetime(2025, 1, 20),
}

deaths_df['date_of_death'] = pd.to_datetime(deaths_df['date_of_death'])
fig, ax = plt.subplots(figsize=(10, 6))
colors = {"Bush": "#d62728", "Obama": "#1f77b4", "Trump 1": "#ff7f0e", "Biden": "#2ca02c", "Trump 2": "#9467bd"}
for admin in ["Bush", "Obama", "Trump 1", "Biden", "Trump 2"]:
    admin_dates = deaths_df.loc[deaths_df['administration'] == admin, 'date_of_death'].sort_values()
    if admin not in admin_start or len(admin_dates) == 0:
        continue
    start = admin_start[admin]
    days = (admin_dates - start).dt.days
    # only include days >= 0 (within admin term window)
    days = days[days >= 0]
    if len(days) == 0:
        continue
    cum = np.arange(1, len(days) + 1)
    ax.step(days, cum, where='post', color=colors[admin], linewidth=2, label=admin)

ax.set_xlabel('Days into administration', fontsize=12, fontweight='bold')
ax.set_ylabel('Cumulative deaths', fontsize=12, fontweight='bold')
ax.legend(frameon=True)
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'Figure3.png'), dpi=300, bbox_inches='tight')
plt.close()

print("All figures generated successfully: Figure1, Figure2 (multi-panel), Figure3 (cumulative)")
