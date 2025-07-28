# %% [markdown]
# # Exploratory Analysis for Chapter 3: Data and Descriptive Analysis
# 
# This cell loads the winsorized firm-level panel, merges ECB inflation series, and generates:
# - Aggregate margins vs. HICP, core, and energy inflation (crisis shading, dual axes)
# - Autocorrelation plot of aggregate margins (Bartlett CI)
# - Correlation matrix of macro variables (+ core inflation, significance stars)
# 
# All plots saved to ../plots/ with standard filenames. You can switch mean/median using AGG_FUNC.

# %%
import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
import warnings, sys

warnings.filterwarnings('ignore')

# --- Paths and settings ---
DATA_PATH  = Path("../data/data_ready/merged_panel_winsorized.parquet")
PLOTS_PATH = Path("../plots")
PLOTS_PATH.mkdir(exist_ok=True)
AGG_FUNC   = "mean"    # Change to "mean" if you want the mean margin series

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("colorblind")
print("Libraries imported – using", AGG_FUNC, "aggregation")

# === Manually-Entered ECB Inflation Series ===
core_inflation_dict = {1996:14.7,1997:15.8,1998:18.2,1999:11.0,2000:3.5,2001:3.7,2002:1.3,2003:0.0,2004:2.4,2005:0.8,2006:0.8,2007:3.1,2008:5.4,2009:0.3,2010:0.7,2011:1.4,2012:2.8,2013:1.5,2014:1.1,2015:0.8,2016:1.2,2017:2.6,2018:1.8,2019:2.3,2020:3.9,2021:3.6,2022:12.5,2023:9.7}
energy_inflation_dict = {2001:10.3,2002:1.9,2003:-0.7,2004:3.7,2005:6.4,2006:9.7,2007:2.2,2008:11.0,2009:2.7,2010:4.3,2011:7.2,2012:7.7,2013:0.6,2014:-3.8,2015:-3.0,2016:-2.5,2017:1.2,2018:3.2,2019:4.8,2020:-1.5,2021:1.7,2022:31.5,2023:25.5}

if not DATA_PATH.is_file():
    sys.exit(f"Data file {DATA_PATH} not found – abort.")

df = pl.read_parquet(DATA_PATH)

# Aggregate mean/median margin by year
if AGG_FUNC == "median":
    agg = (df.group_by("year")
             .agg(pl.col("firm_operating_margin_cal").median().alias("agg_margin"))
             .sort("year").to_pandas())
elif AGG_FUNC == "mean":
    agg = (df.group_by("year")
             .agg(pl.col("firm_operating_margin_cal").mean().alias("agg_margin"))
             .sort("year").to_pandas())
else:
    raise ValueError(f"Unsupported AGG_FUNC: {AGG_FUNC}")


hicp = (df.select("year","mac_hicp_overall_roc")
          .unique().sort("year")
          .to_pandas()
          .rename(columns={'mac_hicp_overall_roc':'hicp'}))

infl = (pd.DataFrame({'year':list(core_inflation_dict),
                      'core':list(core_inflation_dict.values())})
          .merge(pd.DataFrame({'year':list(energy_inflation_dict),
                               'energy':list(energy_inflation_dict.values())}),
                 on='year',how='outer'))

plot_df = (agg.merge(hicp,on='year')
                .merge(infl,on='year',how='left')
                .query("year>=2003 & year<=2023").sort_values("year"))

print("Panel loaded –", len(plot_df), "aggregate years ready")
display(plot_df.head())

# %% [markdown]
# ## Figure 3.1: Aggregate Margins vs. Inflation (with crisis shading)

# %%
fig, ax1 = plt.subplots(figsize=(12,7))
ax1.plot(plot_df["year"], plot_df["agg_margin"].dropna(),
         'ko-', lw=2, label=f"{AGG_FUNC.capitalize()} Operating Margin")
ax1.set_ylabel("Operating Margin (%)", color='k')
ax1.tick_params(axis='y', labelcolor='k')

ax2 = ax1.twinx()
ax2.plot(plot_df["year"], plot_df["hicp"],   'b--s', label="HICP")
ax2.plot(plot_df["year"], plot_df["core"],   'g:^',  label="Core")
ax2.plot(plot_df["year"], plot_df["energy"], 'r-.x', label="Energy")
ax2.set_ylabel("Year‑on‑Year Inflation (%)", color='grey')
ax2.tick_params(axis='y', labelcolor='grey')

for c0,c1 in [(2008,2009),(2020,2020),(2021,2023)]:
    ax1.axvspan(c0-0.5, c1+0.5, color='grey', alpha=0.15)

ax1.set_xlim(plot_df["year"].min()-0.5, plot_df["year"].max()+0.5)
ax1.set_title(f"Aggregate {AGG_FUNC.capitalize()} Operating Margin and Inflation (2003–2023)")
fig.legend(loc='upper left', bbox_to_anchor=(0.08,0.88))
fig.tight_layout()
fig.savefig(PLOTS_PATH/"aggregate_margins_vs_inflation.png", dpi=300)
plt.show()

# %% [markdown]
# ## Figure 3.2: Persistence of Profit Margins (ACF Plot)

# %%
series = plot_df.set_index("year")["agg_margin"].dropna()
fig, ax = plt.subplots(figsize=(9,5))
plot_acf(series, lags=10, alpha=0.05, zero=False, ax=ax)
ax.set_title("Autocorrelation of Aggregate Operating Margin")
fig.tight_layout()
fig.savefig(PLOTS_PATH/"acf_operating_margin.png", dpi=300)
plt.show()

# %% [markdown]
# ## Figure 3.3: Correlation Matrix of Key Macroeconomic Variables (+ Core, + significance stars)

# %%
macro_vars = ['mac_hicp_overall_roc','mac_hicp_pure_energy_roc',
              'mac_cnb_repo_rate_annual','mac_GAP','mac_NLGXQ',
              'mac_ULC','mac_RPMGS']
rename = {'mac_hicp_overall_roc':'HICP','mac_hicp_pure_energy_roc':'Energy HICP',
          'mac_cnb_repo_rate_annual':'Repo','mac_GAP':'Output Gap',
          'mac_NLGXQ':'Prim.Bal','mac_ULC':'ULC','mac_RPMGS':'Import P'}
macro_df = (df.select(macro_vars+['year']).unique()
              .sort('year').to_pandas()
              .drop(columns='year').rename(columns=rename))
macro_df["Core"] = macro_df.index.map(core_inflation_dict).astype(float)
corr = macro_df.corr()

fig, ax = plt.subplots(figsize=(10,8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True,
            cbar_kws={"shrink":0.8}, ax=ax, annot_kws={"size":10})
for y in range(corr.shape[0]):
    for x in range(corr.shape[1]):
        if y != x and abs(corr.iloc[y, x]) > 0.5:
            ax.scatter(x+0.5, y+0.5, s=55, c='black', marker='*')
ax.set_title("Correlation Matrix of Key Macroeconomic Variables")
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
fig.tight_layout()
fig.savefig(PLOTS_PATH/"macro_correlation_heatmap.png", dpi=300)
plt.show()


# %% [markdown]
# ------------------------------------------------------------------
#  EXTRA EDA VISUALS  –  tenure, sector violins, rolling correlation
# ------------------------------------------------------------------

# === Firm Tenure Distribution =====================================
print("Generating Firm‑Tenure distribution …")
firm_tenure = (
    df.group_by("firm_ico")
      .agg(pl.col("year").n_unique().alias("years_in_panel"))
      .to_pandas()
)

max_years = firm_tenure["years_in_panel"].max()
bins = np.arange(0.5, max_years+1.5, 1)

plt.figure(figsize=(12,7))
sns.histplot(firm_tenure, x="years_in_panel", bins=bins, color="C0")
median_tenure = firm_tenure["years_in_panel"].median()
plt.axvline(median_tenure, color="red", ls="--", label=f"Median = {median_tenure:.0f}")
plt.title("Distribution of Firm Tenure in Panel (2000–2023)", fontsize=16)
plt.xlabel("Years with Non‑missing Data")
plt.ylabel("Number of Firms")
plt.xticks(range(1, max_years+1))
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(PLOTS_PATH/"firm_tenure_distribution.png", dpi=300)
plt.show()


# === Sectoral Margin Distributions (Violin) =======================
print("Generating sector‑level violin plots …")
sentinel_years = [2019, 2020, 2021, 2022, 2023]

sector_df = (df.filter(pl.col("year").is_in(sentinel_years))
               .select(["year","level1_nace_en_name","firm_operating_margin_cal"])
               .drop_nulls()
               .to_pandas())

# Focus on the eight most‑represented sectors
top8 = (sector_df["level1_nace_en_name"]
          .value_counts()
          .nlargest(8).index)
sector_df = sector_df[sector_df["level1_nace_en_name"].isin(top8)].copy()

# Clamp extreme values for cleaner violins
sector_df["firm_operating_margin_cal"] = sector_df["firm_operating_margin_cal"].clip(-40, 40)

# Order sectors by overall median margin (descending)
order = (sector_df.groupby("level1_nace_en_name")["firm_operating_margin_cal"]
                   .median()
                   .sort_values(ascending=False)
                   .index)

fig, axes = plt.subplots(len(sentinel_years), 1, figsize=(14, 20), sharex=True)
fig.suptitle("Operating Margin Distribution by Sector (Top 8 Sectors)", fontsize=18, y=1.02)

for i, yr in enumerate(sentinel_years):
    ax = axes[i]
    yr_data = sector_df[sector_df["year"] == yr]
    sns.violinplot(ax=ax, data=yr_data,
                   x="level1_nace_en_name", y="firm_operating_margin_cal",
                   order=order, inner="quartile", scale="width", palette="viridis")
    ax.set_title(f"Year {yr}", fontsize=14)
    ax.set_ylabel("Operating Margin (%)")
    ax.axhline(0, ls="--", c="red", alpha=0.6)
    ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig(PLOTS_PATH/"sectoral_margin_violins.png", dpi=300)
plt.show()


# === 5‑Year Rolling Correlation (Margin vs HICP) ==================
print("Generating rolling correlation plot …")
roll_df = plot_df[["year", "agg_margin", "hicp"]].set_index("year")
roll_df["rolling_corr"] = roll_df["agg_margin"].rolling(window=5).corr(roll_df["hicp"])

plt.figure(figsize=(12,7))
plt.plot(roll_df.index, roll_df["rolling_corr"], "o-", color="purple")
plt.axhline(0, c="black", ls="--")
plt.axhline(0.3, c="grey", ls=":", alpha=0.6)
plt.axhline(-0.3, c="grey", ls=":", alpha=0.6)
plt.ylim(-1, 1)
plt.title("5‑Year Rolling Correlation – Operating Margin vs. HICP Inflation", fontsize=16)
plt.xlabel("Year (end of 5‑yr window)")
plt.ylabel("Correlation Coefficient")
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(PLOTS_PATH/"rolling_correlation_margin_hicp.png", dpi=300)
plt.show()

print("✓  Extra EDA figures saved in", PLOTS_PATH.resolve())

# %%
