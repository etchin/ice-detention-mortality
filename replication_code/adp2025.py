import pandas as pd

file_path = "totalDetained.csv"
df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")

# remove commas
df["Total_num"] = (
    df["Total"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(int)
)

# Define FY 2025 and calendar year 2025 date ranges

start_fy2025 = pd.Timestamp("2024-10-01")
end_fy2025   = pd.Timestamp("2025-09-30")

start_cy2025 = pd.Timestamp("2025-01-01")
end_cy2025   = pd.Timestamp("2025-12-31")

mask_fy2025 = (df["Date"] >= start_fy2025) & (df["Date"] <= end_fy2025)
mask_cy2025 = (df["Date"] >= start_cy2025) & (df["Date"] <= end_cy2025)

df_fy2025 = df[mask_fy2025]
df_cy2025 = df[mask_cy2025]

# 5. Compute averages
fy2025_avg = df_fy2025["Total_num"].mean()
cy2025_avg = df_cy2025["Total_num"].mean()

print("Number of observations in FY 2025:", len(df_fy2025))
print("Number of observations in calendar 2025:", len(df_cy2025))

print(f"FY 2025 average total detained (Oct 1, 2024 – Sep 30, 2025): {fy2025_avg:.2f}")
print(f"Calendar 2025 average total detained (Jan 1 – Dec 31, 2025; based on rows in file): {cy2025_avg:.2f}")
