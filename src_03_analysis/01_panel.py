# %% [markdown]
# # Panel Analysis: Firm-Level Margins and Macro Shocks (v3 - Academically Robust)
#
# **Objective**: Analyze how firm-level margins systematically respond to cost shocks and macro policy through robust dynamic panel models.
#
# **Data**: Annual panel 2003-2023.
#
# **Methodology**:
# 1.  **Winsorization**: Handle extreme outliers in key financial ratios.
# 2.  **Corrected Model Specification**: Use a theoretically sound Error Correction Model (ECM), removing mechanically correlated and time-invariant variables.
# 3.  **Heterogeneity Analysis**:
#     * **Leverage**: Test the balance sheet channel of monetary policy.
#     * **Sector**: Examine differences in responses across major NACE sectors.
# 4.  **Event Study**: Analyze the unique 2021-22 inflation episode.
# 5.  **Robustness Checks**: Validate findings using alternative specifications.

# %%
# Library imports and constants
import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from linearmodels import PanelOLS, IV2SLS
from statsmodels.iolib.summary2 import summary_col
import warnings

warnings.filterwarnings('ignore')

# Enhanced plotting settings for publication quality
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")
plt.rcParams.update({
    'font.size': 12,
    'figure.dpi': 300,
    'savefig.bbox': 'tight'
})

# Constants
DATA_PATH = Path("../data/data_ready/merged_panel_winsorized.parquet")
RESULTS_PATH = Path("../reports/")
PLOTS_PATH = Path("../plots/")
MIN_YEARS_FIRM = 4
YEAR_START = 2003
YEAR_END = 2023
FIRM_ID_COL = "firm_ico"

# Create directories if they don't exist
RESULTS_PATH.mkdir(exist_ok=True)
PLOTS_PATH.mkdir(exist_ok=True)

print(f"Data path: {DATA_PATH}")
print(f"Analysis period: {YEAR_START}-{YEAR_END}")


# %% [markdown]
# ## 1. Load & Final Clean
#
# Load the pre-processed panel data and apply final filters for the analysis.

# %%
# Load the panel data using Polars for efficiency
print(f"Loading data from: {DATA_PATH}")
df_lazy = pl.scan_parquet(DATA_PATH)

# Apply initial filters for the relevant period and required variables
df_panel = (
    df_lazy
    .filter(pl.col("year").is_between(YEAR_START, YEAR_END))
    .filter(pl.col("firm_operating_margin_cal").is_not_null())
    .collect()
)

# Filter for firms with a sufficient number of observations
firm_counts = df_panel.group_by(FIRM_ID_COL).count()
firms_to_keep = firm_counts.filter(pl.col("count") >= MIN_YEARS_FIRM).select(FIRM_ID_COL)
df_panel_filtered = df_panel.join(firms_to_keep, on=FIRM_ID_COL, how="inner")

print(f"Shape after initial filtering: {df_panel_filtered.shape}")
print(f"Unique firms retained: {df_panel_filtered[FIRM_ID_COL].n_unique():,}")


# %% [markdown]
# ## 2. Variable Engineering & Cleaning
#
# This section contains the most critical data preparation steps based on our analysis:
# 1.  **Define Macro Shocks**: Use direct, theory-guided macro variables.
# 2.  **Create Model Variables**: Construct the dependent variable, lags for the ECM, and firm-level controls.
# 3.  **Calculate Leverage**: Create the leverage ratio for heterogeneity analysis.
# 4.  **Winsorize Data**: Critically, clip outliers in the firm-level variables *before* running regressions.

# %%
print("="*60)
print("CONSTRUCTING & CLEANING MODEL VARIABLES")
print("="*60)

# --- 2.1. Define Macro Shocks ---
primary_shocks = {
    'inflation_rate': 'mac_hicp_overall_roc',
    'policy_rate': 'mac_cnb_repo_rate_annual',
    'unit_labor_cost': 'mac_ULC_pct',
    'import_price': 'mac_RPMGS_pct',                # External cost pressure (full time window)
    'fx_rate': 'mac_fx_czk_eur_annual_avg_pct'
}

available_shocks = {k: v for k, v in primary_shocks.items() if v in df_panel_filtered.columns}
print("Using the following macro shocks:")
for name, var in available_shocks.items():
    print(f"  - {name}: `{var}`")


# --- 2.2. Create Core Model & Leverage Variables ---
df_final = (
    df_panel_filtered
    .sort(FIRM_ID_COL, "year")
    .with_columns([
        # OUTCOME: First-difference of the operating margin
        pl.col("firm_operating_margin_cal").diff(1).over(FIRM_ID_COL).alias("d_operating_margin"),

        # ECM TERM 1: Lagged LEVEL of the operating margin
        pl.col("firm_operating_margin_cal").shift(1).over(FIRM_ID_COL).alias("l_operating_margin"),

        # TIME-VARYING FIRM CONTROL
        (pl.col("year") - pl.col("firm_year_founded")).alias("firm_age"),

        # LEVERAGE RATIO
        pl.when(pl.col("firm_total_liabilities_and_equity") > 0)
        .then((pl.col("firm_total_liabilities_and_equity") - pl.col("firm_equity")) / pl.col("firm_total_liabilities_and_equity"))
        .otherwise(None)
        .alias("leverage_ratio")
    ])
    .with_columns([
        # ECM TERM 2: Lagged CHANGE in the operating margin
        pl.col("d_operating_margin").shift(1).over(FIRM_ID_COL).alias("l_d_operating_margin"),
        # LAGGED LEVERAGE (to mitigate simultaneity)
        pl.col("leverage_ratio").shift(1).over(FIRM_ID_COL).alias("leverage_lag")
    ])
    .rename({v: k for k, v in available_shocks.items()})
    .drop_nulls("d_operating_margin")
)

# --- 2.3. Convert to Pandas & Winsorize Outliers ---
df_pd = df_final.to_pandas().set_index([FIRM_ID_COL, 'year'])

print("\n--- Winsorizing data to handle extreme outliers ---")
vars_to_winsorize = ['d_operating_margin', 'l_operating_margin', 'l_d_operating_margin']
for var in vars_to_winsorize:
    lower_bound = df_pd[var].quantile(0.01)
    upper_bound = df_pd[var].quantile(0.99)
    df_pd[var] = df_pd[var].clip(lower=lower_bound, upper=upper_bound)
    print(f"Variable '{var}' clipped between {lower_bound:.2f} and {upper_bound:.2f}")

print("\n--- Descriptive Statistics (Post-Winsorization) ---")
desc_stats = df_pd[vars_to_winsorize].describe().T
print(desc_stats[['mean', 'std', 'min', 'max']].round(3))


# %% [markdown]
# ## 3. Econometric Modeling: Main Results
#
# Our core specification is the **Error Correction Model (ECM)**. It corrects for the issues in the original script and provides a much richer interpretation.
#
# ### Corrected Model Specification
# $$
# \Delta m_{it} = \alpha_i + \gamma_1 m_{i,t-1} + \gamma_2 \Delta m_{i,t-1} + \boldsymbol{\beta}'\mathbf{X}_{t} + \delta \text{firm\_age}_{it} + \epsilon_{it}
# $$
# -   **Removed `cost_ratio`**: To eliminate mechanical correlation.
# -   **Removed `log_employees`**: As it was time-invariant and absorbed by the fixed effects.
# -   **Kept `firm_age`**: As a valid, time-varying control for firm life-cycle effects.

# %%
# --- Define FINAL model specifications ---
dependent = 'd_operating_margin'
firm_controls = ['firm_age'] # Corrected list
macro_shocks = list(available_shocks.keys())

# Define exogenous variables for the models
exog_vars_static = macro_shocks + firm_controls
exog_vars_dynamic = ['l_operating_margin', 'l_d_operating_margin'] + macro_shocks + firm_controls

# Create final regression sample by dropping any remaining missing values
df_reg = df_pd.dropna(subset=[dependent] + exog_vars_dynamic)
print(f"Final regression sample size: {len(df_reg):,} observations")


# --- Model 1: Dynamic Error Correction Model (Preferred Model) ---
print("\n--- [Model 1] Dynamic Error Correction Model (ECM) ---")
mod_ecm = PanelOLS(
    df_reg[dependent],
    df_reg[exog_vars_dynamic],
    entity_effects=True
)
res_ecm = mod_ecm.fit(cov_type='clustered', cluster_entity=True)
print(res_ecm.summary)
print("\n*** ECM Interpretation Note ***")
gamma1 = res_ecm.params['l_operating_margin']
print(f"The speed of adjustment (coefficient on l_operating_margin) is {gamma1:.3f}.")
if gamma1 < 0:
    print("This implies that when a firm's margin is 1pp above its long-run equilibrium, it corrects back down by "
          f"{-gamma1*100:.1f}% in the following year.")


# %% [markdown]
# ## 4. Heterogeneity Analysis
#
# Here, we test if the main relationships change for different types of firms. This adds crucial depth to the analysis.
#
# ### 4.1. The Balance Sheet Channel: High vs. Low Leverage Firms
#
# Does monetary policy (`policy_rate`) have a stronger effect on firms with high debt?

# %%
print("\n" + "="*60)
print("HETEROGENEITY ANALYSIS 1: LEVERAGE & MONETARY POLICY")
print("="*60)

# Create leverage groups for firms where we have the data
df_leverage = df_pd.dropna(subset=['leverage_lag'])
median_leverage = df_leverage['leverage_lag'].median()
df_leverage['leverage_group'] = np.where(df_leverage['leverage_lag'] > median_leverage, 'High Leverage', 'Low Leverage')
print(f"Splitting firms by median leverage of {median_leverage:.2f}")

leverage_results = {}
for group in ['High Leverage', 'Low Leverage']:
    df_group = df_leverage[df_leverage['leverage_group'] == group]
    if len(df_group) > 1000:
        print(f"\n--- Running ECM for: {group} Firms (N={len(df_group):,}) ---")
        mod = PanelOLS(df_group[dependent], df_group[exog_vars_dynamic], entity_effects=True)
        leverage_results[group] = mod.fit(cov_type='clustered', cluster_entity=True)
        # Print the key coefficient for policy rate
        print(leverage_results[group].params.filter(like='policy_rate'))

# --- Visualization of Leverage Heterogeneity ---
fig, ax = plt.subplots(figsize=(8, 6))
leverage_coeffs = pd.DataFrame({
    'Coefficient': {k: v.params['policy_rate'] for k, v in leverage_results.items()},
    'Std. Error': {k: v.std_errors['policy_rate'] for k, v in leverage_results.items()},
}).reset_index().rename(columns={'index': 'Group'})

ax.errorbar(y=leverage_coeffs['Group'], x=leverage_coeffs['Coefficient'], xerr=1.96 * leverage_coeffs['Std. Error'],
            fmt='o', color='darkred', ecolor='salmon', elinewidth=3, capsize=5, ms=10)
ax.axvline(x=0, linestyle='--', color='black', alpha=0.7)
ax.set_title('Monetary Policy Effect by Firm Leverage', fontsize=16, fontweight='bold')
ax.set_xlabel('Coefficient on Policy Rate')
ax.set_ylabel('Leverage Group')
plt.tight_layout()
plt.savefig(PLOTS_PATH / "heterogeneity_leverage_plot.png")
plt.show()

# %% [markdown]
# ### 4.2. Sectoral Differences
#
# Are certain industries more sensitive to macro shocks?

# %%
print("\n" + "="*60)
print("HETEROGENEITY ANALYSIS 2: BY NACE SECTOR")
print("="*60)

# Identify top 5 largest sectors by observation count
top_sectors = df_reg['firm_main_nace_code'].value_counts().head(5).index.to_list()
print(f"Analyzing top 5 sectors: {top_sectors}")

sector_results = {}
for sector in top_sectors:
    df_sector = df_reg[df_reg['firm_main_nace_code'] == sector]
    if len(df_sector) > 1000: # Ensure enough data
        mod = PanelOLS(df_sector[dependent], df_sector[exog_vars_dynamic], entity_effects=True)
        sector_results[sector] = mod.fit(cov_type='clustered', cluster_entity=True)
        print(f"\n--- Results for Sector: {sector} (N={len(df_sector):,}) ---")
        print(sector_results[sector].params.filter(like='inflation_rate'))


# %% [markdown]
# ## 5. Final Visualizations & Results Export
#
# We export a clean summary table of our main models for the paper.

# %%
print("\n--- EXPORTING FINAL RESULTS TABLE ---")

# Add a Static FE model for comparison
mod_static = PanelOLS(df_reg[dependent], df_reg[exog_vars_static], entity_effects=True)
res_static = mod_static.fit(cov_type='clustered', cluster_entity=True)

# Manually construct a summary DataFrame since summary_col is incompatible with linearmodels.PanelOLS results
def extract_results(res, model_name):
    params = res.params
    std_err = res.std_errors
    tstats = params / std_err
    pvals = res.pvalues
    out = pd.DataFrame({
        f'{model_name} Coef.': params,
        f'{model_name} Std.Err.': std_err,
        f'{model_name} t-stat': tstats,
        f'{model_name} p-value': pvals
    })
    return out

summary_static = extract_results(res_static, "Static FE")
summary_ecm = extract_results(res_ecm, "Dynamic ECM")

results_summary = pd.concat([summary_static, summary_ecm], axis=1)
print(results_summary.round(3))

results_path_csv = RESULTS_PATH / "final_panel_results.csv"
#results_summary.round(4).to_csv(results_path_csv)
#print(f"\n✓ Final results table saved to {results_path_csv}")
# %%


