# %% [markdown]
# # Panel Analysis: Firm-Level Margins and Macro Shocks (v5 - Comprehensive)
#
# **Objective**: Analyze how firm-level margins systematically respond to cost shocks and macro policy through robust dynamic panel models, controlling for key firm and sector characteristics.
#
# **Data**: Annual panel 2003-2023.
#
# **Methodology**:
# 1.  **Enriched Model Specification**: Use a theoretically sound Error Correction Model (ECM) with a comprehensive set of controls.
# 2.  **Endogenous Structural Break Test**: Formally test for a structural change in the inflation-margin relationship using a sup-F test to justify the focus on the 2021-2023 period.
# 3.  **Event Study & Robustness**: Analyze the unique 2021-2023 inflation episode using an interaction model, validated with sub-sample analysis and sensitivity checks.
# 4.  **Robust Inference**: Employ Driscoll-Kraay and Two-Way Clustered standard errors to account for cross-sectional dependence.
# 5.  **Heterogeneity Analysis**: Examine differences in responses across NACE sectors to identify varied pass-through mechanisms.
# 6.  **Macroeconomic Context**: Decompose aggregate inflation into profit and labor cost contributions using a GVA framework.

# %%
# Library imports and constants
import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from linearmodels import PanelOLS
import warnings
import statsmodels.api as sm

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

# ------------------------------------------------------------------
# 0.  MANUALLY‑ENTERED HICP SERIES  (ECB SDW – annual averages, % YoY)
#      • core_inflation_rate  = HICP All-items excluding energy (ICP.A.CZ.N.XE0000.4.AVR)
#      • energy_inflation_rate = HICP energy component HICP - Energy (ICP.A.CZ.N.NRGY00.4.AVR)
# ------------------------------------------------------------------
core_inflation_dict = {
    1996: 14.7, 1997: 15.8, 1998: 18.2, 1999: 11.0, 2000: 3.5,
    2001:  3.7, 2002:  1.3, 2003:  0.0, 2004:  2.4, 2005: 0.8,
    2006:  0.8, 2007:  3.1, 2008:  5.4, 2009: 0.3, 2010: 0.7,
    2011:  1.4, 2012:  2.8, 2013:  1.5, 2014: 1.1, 2015: 0.8,
    2016:  1.2, 2017:  2.6, 2018:  1.8, 2019: 2.3, 2020: 3.9,
    2021:  3.6, 2022: 12.5, 2023:  9.7, 2024: 2.7
}

energy_inflation_dict = {
    2001: 10.3, 2002:  1.9, 2003: -0.7, 2004:  3.7, 2005:  6.4,
    2006:  9.7, 2007:  2.2, 2008: 11.0, 2009:  2.7, 2010:  4.3,
    2011:  7.2, 2012:  7.7, 2013:  0.6, 2014: -3.8, 2015: -3.0,
    2016: -2.5, 2017:  1.2, 2018:  3.2, 2019:  4.8, 2020: -1.5,
    2021:  1.7, 2022: 31.5, 2023: 25.5, 2024: 3.0
}

# Turn them into a DataFrame keyed by 'year'
inflation_annual = (
    pd.DataFrame({
        'year': list(core_inflation_dict.keys()),
        'core_inflation_rate': list(core_inflation_dict.values())
    })
    .merge(
        pd.DataFrame({
            'year': list(energy_inflation_dict.keys()),
            'energy_prices_inflation': list(energy_inflation_dict.values())
        }),
        on='year',
        how='outer'
    )
)
# ------------------------------------------------------------------

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
# ## 2. Variable Engineering
#
# This section constructs all variables for the econometric models. Key changes include:
# * **Firm Size & Leverage**: We add controls for firm size (`log_total_assets`) and financial leverage.
# * **Sectoral Wages**: We replace the national `unit_labor_cost` with a more precise measure of `sector_level1_avg_wages_by_nace` growth.

# %%
print("="*60)
print("CONSTRUCTING & CLEANING MODEL VARIABLES (Corrected Wage Growth)")
print("="*60)

# --- Step 1: Create a clean, de-duplicated time series of sectoral wages ---
wage_ts = (
    df_panel_filtered
    .select(["year", "level1_nace_code", "sector_level1_avg_wages_by_nace"])
    .unique()
    .sort("level1_nace_code", "year")
)

# --- Step 2: Calculate the YoY growth rate correctly on the clean time series ---
wage_ts_growth = wage_ts.with_columns(
    (
        pl.col("sector_level1_avg_wages_by_nace").pct_change(1).over("level1_nace_code") * 100
    ).alias("sector_wage_growth")
)

# --- Step 3: Define Macro Shocks Map ---
macro_shocks_map = {
    'inflation_rate': 'mac_hicp_overall_roc',
    'policy_rate': 'mac_cnb_repo_rate_annual',
    'import_price': 'mac_RPMGS_pct',
    'fx_rate': 'mac_fx_czk_eur_annual_avg_pct',
    'output_gap': 'mac_GAP',
    'fiscal_balance': 'mac_NLGXQ'
}

# --- Step 4: Build the final DataFrame by joining the corrected wage growth ---
df_final = (
    df_panel_filtered
    # Join the correctly calculated wage growth back to the main panel
    .join(
        wage_ts_growth.select(["year", "level1_nace_code", "sector_wage_growth"]),
        on=["year", "level1_nace_code"],
        how="left"
    )
    .sort(FIRM_ID_COL, "year") # Sort by firm and year for firm-level calcs
    .with_columns([
        # OUTCOME: First-difference of the operating margin
        pl.col("firm_operating_margin_cal").diff(1).over(FIRM_ID_COL).alias("d_operating_margin"),

        # ECM TERM 1: Lagged LEVEL of the operating margin
        pl.col("firm_operating_margin_cal").shift(1).over(FIRM_ID_COL).alias("l_operating_margin"),

        # FIRM-LEVEL CONTROLS
        (pl.col("year") - pl.col("firm_year_founded")).alias("firm_age"),
        pl.col("firm_total_assets").log().alias("log_assets"),
        pl.when(pl.col("firm_total_liabilities_and_equity") > 0)
        .then((pl.col("firm_total_liabilities_and_equity") - pl.col("firm_equity")) / pl.col("firm_total_liabilities_and_equity"))
        .otherwise(None)
        .alias("leverage_ratio"),

        # sales growth 
        (pl.col("firm_sales_revenue").log().diff(1).over(FIRM_ID_COL)*100).alias("sales_growth"),

    ])
    .with_columns([
        # ECM TERM 2: Lagged CHANGE in the operating margin
        pl.col("d_operating_margin").shift(1).over(FIRM_ID_COL).alias("l_d_operating_margin"),
        
        # Lagged firm controls to mitigate simultaneity
        pl.col("leverage_ratio").shift(1).over(FIRM_ID_COL).alias("l_leverage_ratio"),
        pl.col("log_assets").shift(1).over(FIRM_ID_COL).alias("l_log_assets"),
    ])
    .rename({v: k for k, v in macro_shocks_map.items()})
    .drop_nulls("d_operating_margin")
)

# --- Step 5: Convert to Pandas & Winsorize Outliers ---
df_pd = df_final.to_pandas().set_index([FIRM_ID_COL, 'year'])

print("\n--- Winsorizing data to handle extreme outliers ---")
vars_to_winsorize = [
    'd_operating_margin', 'l_operating_margin', 'l_d_operating_margin',
    'l_leverage_ratio', 'l_log_assets', 'sales_growth'
]
for var in vars_to_winsorize:
    if var in df_pd.columns:
        # Important: drop NaNs before calculating quantiles
        valid_data = df_pd[var].dropna()
        if not valid_data.empty:
            lower_bound = valid_data.quantile(0.01)
            upper_bound = valid_data.quantile(0.99)
            df_pd[var] = df_pd[var].clip(lower=lower_bound, upper=upper_bound)
            print(f"Variable '{var}' clipped between {lower_bound:.2f} and {upper_bound:.2f}")

print("\n--- Descriptive Statistics (Post-Winsorization) ---")
print(df_pd[vars_to_winsorize].describe().T[['mean', 'std', 'min', 'max']].round(3))


# %% [markdown]
# ## 3. Model Specification
#
# This section defines the dependent and independent variables used throughout the analysis. This centralizes the model specification, ensuring consistency across all subsequent tests.

# %%

# Attach annual inflation figures to each firm‑year observation
df_pd = (
    df_pd
        .reset_index()                                 # 1 bring 'year' out of MultiIndex
        .merge(inflation_annual, on='year', how='left')
        .set_index([FIRM_ID_COL, 'year'])
)

# --- DEFINE ALL MODEL VARIABLES CENTRALLY ---
dependent = 'd_operating_margin'

# Define components of the model
dynamic_terms = ['l_operating_margin', 'l_d_operating_margin']
firm_controls = ['firm_age', 'l_log_assets', 'l_leverage_ratio', 'sales_growth']
sector_controls = ['sector_wage_growth']

# --- Create different sets of macro shocks for robustness checks ---
# Base set of macro shocks excluding any general inflation measure
macro_shocks_base = ['policy_rate', 'import_price', 'fx_rate', 
                     'energy_prices_inflation', 'output_gap', 'fiscal_balance']

# Specification with headline inflation
macro_shocks_headline = macro_shocks_base + ['inflation_rate']

# Preferred specification with core inflation
macro_shocks_core = macro_shocks_base + ['core_inflation_rate']


# --- Define full regressor lists for different models ---
# Final, preferred model specification using core inflation
exog_vars_final = dynamic_terms + macro_shocks_core + firm_controls + sector_controls

# Parsimonious set for the structural break test (using headline inflation)
exog_vars_break_test = dynamic_terms + ['inflation_rate', 'policy_rate'] + firm_controls + sector_controls

print("Model variable lists defined for headline and core specifications.")


# %% [markdown]
# ## 4. Justification: Endogenous Structural Break Test (Sup-F Test)
#
# Before analyzing the 2021-2023 period, we first formally test for the presence of a structural break in the relationship between inflation and profit margins. We use the Andrews (1993) sup-F test to endogenously identify the most likely break date, which provides a data-driven justification for our focus on the recent episode.

# %%
print("\n" + "="*60)
print("RUNNING ENDOGENOUS STRUCTURAL BREAK TEST (SUP-F)")
print("="*60)

# --- Create the sample for the break test ---
df_break_test_base = df_pd.dropna(subset=[dependent] + exog_vars_break_test)

# --- Test 1: Full Sample Analysis (2003-2023) ---
print("\n--- [Test 1] Full Sample Analysis ---")
df_break_test_full = df_break_test_base.sort_index(level='year')
years = df_break_test_full.index.get_level_values('year').unique().sort_values()

trim_frac = 0.15
start_year = years[int(len(years) * trim_frac)]
end_year = years[int(len(years) * (1 - trim_frac))]
potential_break_years = range(start_year, end_year + 1)
print(f"Testing for a break in the years: {list(potential_break_years)}")

f_statistics = []
for break_year in potential_break_years:
    df_temp = df_break_test_full.copy()
    df_temp['post_break'] = (df_temp.index.get_level_values('year') > break_year).astype(int)
    df_temp['inflation_x_break'] = df_temp['inflation_rate'] * df_temp['post_break']
    exog_unrestricted = exog_vars_break_test + ['inflation_x_break']
    df_loop_sample = df_temp.dropna(subset=exog_unrestricted)
    
    mod_unrestricted = PanelOLS(df_loop_sample[dependent], df_loop_sample[exog_unrestricted], entity_effects=True)
    res_unrestricted = mod_unrestricted.fit(cov_type='clustered', cluster_entity=True)
    
    mod_restricted = PanelOLS(df_loop_sample[dependent], df_loop_sample[exog_vars_break_test], entity_effects=True)
    res_restricted = mod_restricted.fit(cov_type='clustered', cluster_entity=True)
    
    ssr_u, ssr_r = res_unrestricted.resid_ss, res_restricted.resid_ss
    q, n, k = 1, res_unrestricted.nobs, res_unrestricted.df_model
    f_stat = ((ssr_r - ssr_u) / q) / (ssr_u / (n - k))
    f_statistics.append({'year': break_year, 'f_stat': f_stat})

if f_statistics:
    results_break_df = pd.DataFrame(f_statistics)
    best_break_year = results_break_df.loc[results_break_df['f_stat'].idxmax()]
    print(f"\nMost Likely Break Year (Full Sample): {int(best_break_year['year'])} with F-statistic: {best_break_year['f_stat']:.2f}")

    # Visualization
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(results_break_df['year'], results_break_df['f_stat'], marker='o', linestyle='-')
    ax.axvline(x=best_break_year['year'], color='red', linestyle='--', label=f"Most Likely Break ({int(best_break_year['year'])})")
    ax.set_title("Sup-F Test for Structural Break in Inflation Coefficient (Full Sample)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Potential Break Year")
    ax.set_ylabel("F-statistic")
    ax.legend()
    plt.savefig(PLOTS_PATH / "structural_break_test_full.png")
    plt.show()

# print statistics for the full sample
print("\n--- Summary of Full Sample Sup-F Test ---")
print(results_break_df.round(4))

# %% 

# ------------------------------------------------------------------
# SECOND PASS: look for an additional break after 2008  -------------
# ------------------------------------------------------------------
df_bt_sub = df_break_test_full[df_break_test_full.index.get_level_values('year') >= 2008]

years_sub = df_bt_sub.index.get_level_values('year').unique().sort_values()
start_sub = years_sub[int(len(years_sub) * trim_frac)]
end_sub   = years_sub[int(len(years_sub) * (1 - trim_frac))]
potential_break_years_sub = range(start_sub, end_sub + 1)

f_stats_sub = []
for by in potential_break_years_sub:
    dft = df_bt_sub.copy()
    dft['post_break'] = (dft.index.get_level_values('year') > by).astype(int)
    dft['inflation_x_break'] = dft['inflation_rate'] * dft['post_break']
    ex_unres = exog_vars_break_test + ['inflation_x_break']
    dft = dft.dropna(subset=ex_unres)
    ru = PanelOLS(dft[dependent], dft[ex_unres], entity_effects=True).fit(cov_type='clustered', cluster_entity=True)
    rr = PanelOLS(dft[dependent], dft[exog_vars_break_test], entity_effects=True).fit(cov_type='clustered', cluster_entity=True)
    f_stats_sub.append({
        'year': by,
        'f_stat': ((rr.resid_ss - ru.resid_ss) / 1) / (ru.resid_ss / (ru.nobs - ru.df_model))
    })

sub_df = pd.DataFrame(f_stats_sub)
best_sub = sub_df.loc[sub_df['f_stat'].idxmax()]
print(f"\nSecondary break (post‑2008 sample): {int(best_sub.year)}  F = {best_sub.f_stat:.2f}")

# %% [markdown]
# ## 5. Main Finding: The 2021-2023 Inflation Spike
#
# The Sup-F test confirms significant structural instability around 2020. We now formally test if the inflation-margin relationship changed during the 2021-2023 episode using two interaction models to ensure robustness.

# %% [markdown]
# ### 5.1 Interaction with Core Inflation (Preferred Model)
#
# This model tests for a structural break in the pass-through of ** core (non-energy) inflation**. It avoids omitted variable bias by keeping `energy_prices_inflation` as a control and eliminates multicollinearity by design. This is our preferred specification.

# %%
from statsmodels.stats.outliers_influence import variance_inflation_factor

print("\n" + "="*60)
print("TESTING FOR STRUCTURAL BREAK: CORE INFLATION")
print("="*60)

# Create the final regression sample based on the full model
df_reg_final = df_pd.dropna(subset=[dependent] + exog_vars_final)
df_interaction = df_reg_final.copy()

# Create dummy and interaction term for core inflation
df_interaction['episode_21_23'] = df_interaction.index.get_level_values('year').isin([2021, 2022, 2023]).astype(int)

df_interaction['episode_dummy'] = df_interaction['episode_21_23'] 

df_interaction['core_x_episode'] = (df_interaction['core_inflation_rate']
                                    * df_interaction['episode_21_23'])

# Exogenous list for core‑inflation interaction model
exog_vars_interaction_core = (dynamic_terms + macro_shocks_core +
                              firm_controls + sector_controls +
                            ['episode_dummy',
                            'core_x_episode'])

# Run the PanelOLS model with Driscoll-Kraay SEs
mod_interaction_core = PanelOLS(
    df_interaction[dependent],
    df_interaction.dropna(subset=exog_vars_interaction_core)[exog_vars_interaction_core],
    entity_effects=True
)
res_interaction_core = mod_interaction_core.fit(cov_type='driscoll-kraay', kernel='bartlett')
print(res_interaction_core.summary)

# %% [markdown]
# ### 5.2 Robustness Check: Interaction with Headline Inflation
#
# This model tests for a break in the pass-through of **headline inflation** while keeping `energy_prices_inflation` as a control. We report Variance Inflation Factors (VIFs) to show that multicollinearity is present but manageable.

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK: HEADLINE INFLATION INTERACTION")
print("="*60)

# Create the interaction term for HEADLINE inflation
df_interaction['inflation_x_episode'] = df_interaction['inflation_rate'] * df_interaction['episode_21_23']

# Define exog variables for the HEADLINE model
exog_vars_interaction_headline = dynamic_terms + macro_shocks_headline + firm_controls + sector_controls + ['inflation_x_episode']

# Run the PanelOLS model
mod_interaction_headline = PanelOLS(
    df_interaction[dependent],
    df_interaction.dropna(subset=exog_vars_interaction_headline)[exog_vars_interaction_headline],
    entity_effects=True
)
res_interaction_headline = mod_interaction_headline.fit(cov_type='driscoll-kraay', kernel='bartlett')
print(res_interaction_headline.summary)

# --- VIF Check for the Headline Interaction Model ---
print("\n--- VIF Check for Headline Interaction Model ---")
vif_data = df_interaction.dropna(subset=exog_vars_interaction_headline)[exog_vars_interaction_headline]
vif_data_const = sm.add_constant(vif_data, prepend=False)

vif_df = pd.DataFrame()
vif_df["Variable"] = vif_data_const.columns
vif_df["VIF"] = [variance_inflation_factor(vif_data_const.values, i) for i in range(vif_data_const.shape[1])]
print(vif_df[vif_df["Variable"] != "const"].sort_values("VIF", ascending=False).round(2))

# %% [markdown]
# ## 6. Robustness Checks for the Episode Analysis
#
# To ensure the finding of a structural break is not an artifact of our specific model or episode definition, we perform three robustness checks.

# %% [markdown]
# ### 6.1 Sub-Sample Analysis

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK 1: SUB-SAMPLE ANALYSIS")
print("="*60)

# CORRECTED: Define a parsimonious model for this check to avoid multicollinearity
exog_vars_subsample = dynamic_terms + ['inflation_rate'] + firm_controls + sector_controls

# Define the two periods on a consistently dropped sample
df_subsample_base = df_pd.dropna(subset=[dependent] + exog_vars_subsample)
df_normal_period = df_subsample_base[df_subsample_base.index.get_level_values('year') <= 2020]
df_shock_period = df_subsample_base[df_subsample_base.index.get_level_values('year') > 2020]

# --- Run Model on Normal Period ---
print(f"\n--- Model for Normal Period (pre-2021) ---")
mod_normal = PanelOLS(df_normal_period[dependent], df_normal_period[exog_vars_subsample], entity_effects=True)
res_normal = mod_normal.fit(cov_type='driscoll-kraay', kernel='bartlett')
print("Coefficient on inflation_rate:", res_normal.params.filter(like='inflation_rate'))

# --- Run Model on Shock Period ---
print(f"\n--- Model for Shock Period (2021-2023) ---")
mod_shock = PanelOLS(df_shock_period[dependent], df_shock_period[exog_vars_subsample], entity_effects=True)
res_shock = mod_shock.fit(cov_type='driscoll-kraay', kernel='bartlett')
print("Coefficient on inflation_rate:", res_shock.params.filter(like='inflation_rate'))


# %% [markdown]
# ### 6.2 Sensitivity to Episode Definition

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK 2: SENSITIVITY TO EPISODE DEFINITION")
print("="*60)

episode_definitions = {
    "2021-2023 (Baseline)": [2021, 2022, 2023],
    "2021-2022 (Core Spike)": [2021, 2022],
    "2022 only (Peak Year)": [2022]
}
results_sensitivity = []

for name, years in episode_definitions.items():
    df_temp = df_reg_final.copy()
    df_temp['episode'] = df_temp.index.get_level_values('year').isin(years).astype(int)
    df_temp['inflation_x_episode'] = df_temp['inflation_rate'] * df_temp['episode']
    
    # use the HEADLINE interaction specification for all alternative episode windows
    exog_temp = [c for c in exog_vars_interaction_headline
                if c not in ['inflation_x_episode', 'episode_21_23']] \
                + ['inflation_x_episode']

    mod_sens = PanelOLS(df_temp[dependent], df_temp.dropna(subset=exog_temp)[exog_temp], entity_effects=True)
    res_sens = mod_sens.fit(cov_type='driscoll-kraay', kernel='bartlett')
    
    interaction_coeff = res_sens.params['inflation_x_episode']
    interaction_pval = res_sens.pvalues['inflation_x_episode']
    
    results_sensitivity.append({
        "Episode Definition": name,
        "Interaction Effect": interaction_coeff,
        "p-value": interaction_pval
    })

results_df = pd.DataFrame(results_sensitivity).set_index("Episode Definition")
print("\n--- Summary of Sensitivity Analysis ---")
print(results_df.round(4))


# %% [markdown]
# ### 6.3 Two-Way Clustered Standard Errors

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK 3: TWO-WAY CLUSTERED STANDARD ERRORS")
print("="*60)

# Re‑estimate the headline‑interaction model with entity & time clustering
res_interaction_tw = mod_interaction_headline.fit(
    cov_type='clustered',
    cluster_entity=True,
    cluster_time=True
)
print("\n--- Interaction Model with Two-Way Clustering ---")
print(res_interaction_tw.summary.tables[1])

print("\n*** Key coefficient check ***")
pval_interaction_tw = res_interaction_tw.pvalues['inflation_x_episode']
print(f"p-value for 'inflation_x_episode' with two-way clustering: {pval_interaction_tw:.4f}")

# %% [markdown]
# ## 7. Final, Fully-Specified Model & Heterogeneity
#
# We now present the main model with all controls, which serves as the basis for the heterogeneity analysis of the pass-through mechanism.

# %%
# --- Run the Final, Fully-Specified ECM with Driscoll-Kraay SEs ---
print("\n--- Final, Fully-Specified ECM Results (Driscoll-Kraay SEs) ---")
mod_final = PanelOLS(
    df_reg_final[dependent],
    df_reg_final[exog_vars_final],
    entity_effects=True
)
res_final_dk = mod_final.fit(cov_type='driscoll-kraay', kernel='bartlett')
print(res_final_dk.summary)

# %%
print("\n" + "="*60)
print("FINAL VERDICT ON COST SHOCKS")
print("="*60)

def flag(p):         # ✓ if <5 %, ✗ otherwise
    return "✓" if p < 0.05 else "✗"

for var_label in ['energy_prices_inflation',
                  'core_inflation_rate',
                  'inflation_rate']:
    if var_label in res_final_dk.params.index:
        beta = res_final_dk.params[var_label]
        pval = res_final_dk.pvalues[var_label]
        nice_name = {'energy_prices_inflation': 'Energy inflation',
                    'core_inflation_rate'    : 'Core (non‑energy) inflation',
                    'inflation_rate'         : 'Headline inflation'}[var_label]
        print(f"{nice_name:25s}: β = {beta: .4f},  p = {pval:.4f}  {flag(pval)}")


# %% [markdown]
# ### 7.1 Heterogeneity Analysis: The Pass-Through Mechanism (CORRECTED)

# %%
print("\n" + "="*60)
print("COMPREHENSIVE NACE LEVEL 2 PASS-THROUGH ANALYSIS")
print("="*60)

# This is the corrected, lean list for THIS specific analysis
exog_vars_passthrough = [
    'l_operating_margin', 'l_d_operating_margin',   # Dynamic Terms
    'firm_age', 'l_log_assets', 'l_leverage_ratio', # Firm Controls
    'sector_wage_growth',                           # Sector Labor Costs
    'policy_rate', 'import_price', 'fx_rate', 'output_gap', 'fiscal_balance', # Macro Controls
    'energy_prices_inflation',                      # The SPECIFIC Cost Shock
    'sector_level2_ppi_by_nace_pct'                 # The SPECIFIC Pass-Through Mechanism
]

# --- Step 1: Identify all sectors meeting the observation threshold ---
MIN_OBS_FOR_SELECTION = 5000
# Ensure df_reg_final is defined based on all necessary variables
df_passthrough_sample = df_pd.dropna(subset=[dependent] + exog_vars_passthrough)

sector_counts = df_passthrough_sample.groupby('level2_nace_code').size()
sectors_to_run = sector_counts[sector_counts >= MIN_OBS_FOR_SELECTION].index.to_list()
print(f"Identified {len(sectors_to_run)} sectors with at least {MIN_OBS_FOR_SELECTION:,} observations.")

# --- Step 2: Run Pass-Through Model on all selected sectors ---
passthrough_results = []
nace_level2_map = df_final.select(['level2_nace_code', 'level2_nace_en_name']).unique().to_pandas().set_index('level2_nace_code')['level2_nace_en_name'].to_dict()

for code in sectors_to_run:
    # No need to dropna again, df_passthrough_sample is already clean for this model
    df_sector = df_passthrough_sample[df_passthrough_sample['level2_nace_code'] == code]
    sector_name = nace_level2_map.get(code, code)
    print(f"\n--- Running Model for Sector: {sector_name} ({code}) ---")

    try:
        mod_pt = PanelOLS(df_sector[dependent], df_sector[exog_vars_passthrough], entity_effects=True)
        res_pt = mod_pt.fit(cov_type='driscoll-kraay', kernel='bartlett')

        passthrough_results.append({
            "Sector": sector_name,
            "Energy Shock Coeff.": res_pt.params.get('energy_prices_inflation', np.nan),
            "p-value (Energy)": res_pt.pvalues.get('energy_prices_inflation', np.nan),
            "Sector PPI Coeff.": res_pt.params.get('sector_level2_ppi_by_nace_pct', np.nan),
            "p-value (PPI)": res_pt.pvalues.get('sector_level2_ppi_by_nace_pct', np.nan)
        })
    except Exception as e:
        print(f"🛑 MODEL FAILED for {sector_name}. Reason: {e}")

# --- Display the results in a final, comprehensive summary table ---
if passthrough_results:
    results_cs_df = pd.DataFrame(passthrough_results).set_index("Sector").sort_values("Energy Shock Coeff.")
    print("\n" + "="*70)
    print("           SUMMARY OF COMPREHENSIVE NACE LEVEL 2 CASE STUDY RESULTS")
    print("="*70)
    print(results_cs_df.round(4))

# %%
print("\n" + "="*60)
print("VIF CHECK FOR FINAL, FULLY-SPECIFIED MODEL")
print("="*60)

# Use the data and variables from the model estimated in the PREVIOUS cell (mod_final)
# That model was run on df_reg_final with exog_vars_final.
vif_data_final = df_reg_final[exog_vars_final]
vif_data_final_const = sm.add_constant(vif_data_final, prepend=False)

vif_df_final = pd.DataFrame()
vif_df_final["Variable"] = vif_data_final_const.columns
vif_df_final["VIF"] = [variance_inflation_factor(vif_data_final_const.values, i) for i in range(vif_data_final_const.shape[1])]

print(vif_df_final[vif_df_final["Variable"] != "const"].sort_values("VIF", ascending=False).round(2))

# %% [markdown]
# ### Final Visualization: Sector Archetypes
#
# This plot is the final piece of evidence. It maps each sector based on its sensitivity to the **energy shock** (x-axis) versus its ability to **raise its own prices** (y-axis, the coefficient on sector PPI). This visually separates the economy into three archetypes:
# * **Pass-Through Champions (Green)**: Insulated from the energy shock and able to raise their own prices.
# * **Squeezed but Resilient (Orange)**: Hurt by the energy shock, but also able to raise prices, suggesting they passed on some costs.
# * **Cost Absorbers / Puzzles (Red)**: All other sectors, including those hurt by energy costs but unable to raise prices.

# %%
# --- Visualization: The Pass-Through Mechanism Scatter Plot ---
if passthrough_results:
    fig, ax = plt.subplots(figsize=(12, 9))

    # Define colors for the three archetypes
    conditions = [
        (results_cs_df['p-value (Energy)'] > 0.05) & (results_cs_df['p-value (PPI)'] < 0.05), # Pass-Through Champions
        (results_cs_df['p-value (Energy)'] < 0.05) & (results_cs_df['p-value (PPI)'] < 0.05), # Squeezed but Resilient
    ]
    choices = ['green', 'orange']
    results_cs_df['Archetype'] = np.select(conditions, choices, default='darkred') # Cost Absorbers / Puzzles

    # Create the scatter plot
    sns.scatterplot(
        data=results_cs_df,
        x='Energy Shock Coeff.',
        y='Sector PPI Coeff.',
        hue='Archetype',
        palette={'green': 'green', 'orange': 'orange', 'darkred': 'darkred'},
        s=150,
        alpha=0.8,
        ax=ax
    )

    # Add labels
    for i, row in results_cs_df.iterrows():
        ax.text(row['Energy Shock Coeff.'] + 0.005, row['Sector PPI Coeff.'], i, fontsize=9)

    ax.axvline(x=0, color='black', linestyle=':', alpha=0.5)
    ax.axhline(y=0, color='black', linestyle=':', alpha=0.5)
    
    ax.set_xlabel('Energy Shock Impact (Margin Squeeze)')
    ax.set_ylabel('Pass-Through Ability (PPI Coefficient)')
    ax.set_title('Sector Archetypes: Mapping the Energy Crisis Response', fontsize=16, fontweight='bold')

    # Update legend
    handles, labels = ax.get_legend_handles_labels()
    label_map = {'green': 'Pass-Through Champions', 'orange': 'Squeezed but Resilient', 'darkred': 'Cost Absorbers / Puzzles'}
    ax.legend(handles, [label_map[l] for l in labels], title='Archetype')
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / "final_passthrough_archetypes.png")
    plt.show()

# %% [markdown]
# ## 8. Macro-Level Analysis: GVA Decomposition
#
# As a final step, we perform a standard macroeconomic accounting exercise to decompose domestic inflation (the GVA deflator) into contributions from labor costs and profits. This provides context for the firm-level findings.
#
# **Note:** The following code uses placeholder data. You must replace it with actual quarterly, non-seasonally adjusted data from the Czech Statistical Office (CZSO) for GVA, Compensation of Employees, and Gross Operating Surplus.

# %%
# --- GVA DECOMPOSITION ANALYSIS ---
print("\n" + "="*60)
print("MACRO ANALYSIS: GVA DECOMPOSITION")
print("="*60)

# --- Step 1: Obtain and format the data from CZSO ---
# !!! IMPORTANT: THIS IS PLACEHOLDER DATA !!!
# You MUST replace this with actual quarterly, non-seasonally adjusted data.
# GVA = Gross Value Added (Nominal)
# WAGES = Compensation of Employees (Nominal)
# GOS = Gross Operating Surplus & Mixed Income (Nominal)
# GVA_REAL = Gross Value Added (Real, e.g., in 2015 prices)

data = {
    'GVA': [1200, 1250, 1300, 1350, 1250, 1300, 1350, 1400],
    'WAGES': [600, 620, 640, 660, 630, 650, 670, 690],
    'GOS': [500, 525, 550, 575, 520, 545, 570, 595],
    'GVA_REAL': [1000, 1020, 1040, 1060, 1010, 1030, 1050, 1070]
}
dates = pd.to_datetime(['2021-03-31', '2021-06-30', '2021-09-30', '2021-12-31',
                          '2022-03-31', '2022-06-30', '2022-09-30', '2022-12-31'])
national_accounts = pd.DataFrame(data, index=dates)

# --- Step 2: Calculate the GVA deflator and component contributions ---
# GVA Deflator (P) = Nominal GVA / Real GVA
national_accounts['GVA_DEFLATOR'] = national_accounts['GVA'] / national_accounts['GVA_REAL']

# Year-over-year change in the deflator (our measure of domestic inflation)
# Note: use .pct_change(4) for quarterly data, .pct_change(1) for annual data.
national_accounts['GVA_DEFLATOR_YOY'] = national_accounts['GVA_DEFLATOR'].pct_change(4) * 100

# Calculate unit labour costs (ULC) and unit profits (UP) contributions
national_accounts['ULC_CONTRIBUTION'] = (national_accounts['WAGES'].pct_change(4) * (national_accounts['WAGES'].shift(4) / national_accounts['GVA'].shift(4))) * 100
national_accounts['GOS_CONTRIBUTION'] = (national_accounts['GOS'].pct_change(4) * (national_accounts['GOS'].shift(4) / national_accounts['GVA'].shift(4))) * 100

print("--- GVA Decomposition Results (Placeholder Data) ---")
print(national_accounts[['GVA_DEFLATOR_YOY', 'ULC_CONTRIBUTION', 'GOS_CONTRIBUTION']].dropna().round(2))

# --- Step 3: Visualize the decomposition ---
plot_data = national_accounts[['GVA_DEFLATOR_YOY', 'ULC_CONTRIBUTION', 'GOS_CONTRIBUTION']].dropna()

fig, ax = plt.subplots(figsize=(12, 7))
plot_data[['ULC_CONTRIBUTION', 'GOS_CONTRIBUTION']].plot(
    kind='bar',
    stacked=True,
    ax=ax,
    label=['Unit Labour Costs', 'Unit Profits']
)
ax.plot(plot_data.index, plot_data['GVA_DEFLATOR_YOY'], color='black', marker='o', label='GVA Deflator (YoY Inflation)')

ax.set_ylabel("Percentage Points Contribution to YoY Inflation")
ax.set_title("Decomposition of Domestic Inflation (GVA Deflator)", fontsize=16, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(PLOTS_PATH / "gva_decomposition.png")
plt.show()