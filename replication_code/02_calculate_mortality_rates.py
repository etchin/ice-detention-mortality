import pandas as pd
import numpy as np
from scipy import stats

import os
base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
deaths_df = pd.read_csv(os.path.join(base_dir, "complete_death_records.csv"))
adp_df = pd.read_csv(os.path.join(base_dir, "average_daily_population.csv"))

def calculate_poisson_ci(deaths, person_years, confidence=0.95):
    alpha = 1 - confidence
    lower = 0 if deaths == 0 else stats.chi2.ppf(alpha/2, 2*deaths) / (2 * person_years) * 100000
    upper = stats.chi2.ppf(1 - alpha/2, 2*(deaths+1)) / (2 * person_years) * 100000
    return lower, upper

# Define correct fiscal year ranges for each administration
admin_fy_ranges = {
    "Bush": (2004, 2008),
    "Obama": (2009, 2016),
    "Trump 1": (2017, 2020),
    "Biden": (2021, 2024),
    "Trump 2": (2025, 2025)
}

# Validate that the 'administration' field is assigned by actual date of death
from datetime import datetime

cutpoints = [
    ("Bush", datetime(2001, 1, 20), datetime(2009, 1, 19)),
    ("Obama", datetime(2009, 1, 20), datetime(2017, 1, 19)),
    ("Trump 1", datetime(2017, 1, 20), datetime(2021, 1, 19)),
    ("Biden", datetime(2021, 1, 20), datetime(2025, 1, 19)),
    ("Trump 2", datetime(2025, 1, 20), datetime(2025, 9, 30)),
]

def admin_by_date(d):
    for name, start, end in cutpoints:
        if start <= d <= end:
            return name
    return None

deaths_df['date_of_death'] = pd.to_datetime(deaths_df['date_of_death'])
deaths_df['admin_by_date'] = deaths_df['date_of_death'].apply(admin_by_date)
if not (deaths_df['admin_by_date'] == deaths_df['administration']).all():
    mismatches = deaths_df.loc[deaths_df['admin_by_date'] != deaths_df['administration'], ['date_of_death','administration','admin_by_date']]
    raise ValueError(f"Administration assignment mismatch for some rows based on date-of-death.\n{mismatches.head()}\nPlease ensure 'administration' is assigned by date of death.")

results = []
for admin, (start_fy, end_fy) in admin_fy_ranges.items():
    admin_deaths = deaths_df[deaths_df["administration"] == admin]
    death_count = len(admin_deaths)
    
    admin_adp = adp_df[(adp_df["fiscal_year"] >= start_fy) & (adp_df["fiscal_year"] <= end_fy)]
    person_years = admin_adp["adp"].sum()
    
    rate = (death_count / person_years) * 100000
    ci_lower, ci_upper = calculate_poisson_ci(death_count, person_years)
    
    results.append({
        "administration": admin,
        "deaths": death_count,
        "person_years": person_years,
        "rate_per_100k": rate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    })

results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(base_dir, "mortality_rates_by_administration.csv"), index=False)
print(results_df.to_string(index=False))
