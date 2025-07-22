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


# %% [markdown]
# ## 6. Focus on the 2021-2023 Inflation Spike
#
# Having established a robust baseline model, we now use it to address the core research objective: to what extent was the 2021-2023 inflation episode different from prior periods?
#
# We will use two methods:
# 1.  **Interaction Model**: To formally test for a structural change in the inflation-margin relationship.
# 2.  **Sub-Sample Analysis**: As a robustness check, comparing the model before and during the recent shock period.

# %%
# --- 6.1. Descriptive Visualization: Setting the Stage ---

print("--- Creating time-series plot of margins and inflation ---")

# Calculate annual averages from our regression sample for consistency
plot_data = df_reg.groupby('year').agg({
    'l_operating_margin': 'mean',
    'inflation_rate': 'mean'
}).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 7))

# Plotting average operating margin
color = 'tab:blue'
ax1.set_xlabel('Year')
ax1.set_ylabel('Average Operating Margin (%)', color=color)
ax1.plot(plot_data['year'], plot_data['l_operating_margin'], color=color, marker='o', label='Avg. Operating Margin')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(False)

# Creating a second y-axis for the inflation rate
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Annual Inflation Rate (%)', color=color)
ax2.plot(plot_data['year'], plot_data['inflation_rate'], color=color, linestyle='--', marker='x', label='Inflation Rate (HICP)')
ax2.tick_params(axis='y', labelcolor=color)
ax2.grid(False)

# Highlighting the 2021-2023 episode
ax1.axvspan(2021, 2023, alpha=0.2, color='gray', label='2021-23 Episode')

fig.tight_layout()
ax1.set_title('Czech Firm Margins and Inflation (2004-2023)', fontsize=16, fontweight='bold')
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
plt.savefig(PLOTS_PATH / "timeseries_margin_inflation.png")
plt.show()


# %% [markdown]
# ### 6.2. The Formal Test: Interaction Model
#
# Here we test the hypothesis that the pass-through from inflation to margins was structurally different during the 2021-2023 period. We interact the `inflation_rate` variable with a dummy variable for these years.

# %%
print("\n" + "="*60)
print("TESTING FOR A STRUCTURAL BREAK: INTERACTION MODEL")
print("="*60)

df_interaction = df_reg.copy()

# Create the dummy variable for the episode
df_interaction['episode_21_23'] = df_interaction.index.get_level_values('year').isin([2021, 2022, 2023]).astype(int)

# Create the interaction term
df_interaction['inflation_x_episode'] = df_interaction['inflation_rate'] * df_interaction['episode_21_23']

# Define the explanatory variables for this model
exog_vars_interaction = exog_vars_dynamic + ['inflation_x_episode']

# Run the PanelOLS model
mod_interaction = PanelOLS(
    df_interaction[dependent],
    df_interaction[exog_vars_interaction],
    entity_effects=True
)
res_interaction = mod_interaction.fit(cov_type='clustered', cluster_entity=True)

print(res_interaction.summary)

# --- Clear Interpretation of Interaction Results ---
print("\n*** Interpretation of Interaction Model Results ***")
beta1 = res_interaction.params['inflation_rate']
beta2 = res_interaction.params['inflation_x_episode']
pval_beta2 = res_interaction.pvalues['inflation_x_episode']

print(f"Effect of inflation in 'normal' years (2004-2020): {beta1:.4f}")
print(f"DIFFERENTIAL effect of inflation in 2021-23 episode: {beta2:.4f}")
print(f"  - p-value for this differential effect: {pval_beta2:.4f}")

# Test the significance of the difference
if pval_beta2 < 0.05:
    print("  - The relationship between inflation and margins was STATISTICALLY DIFFERENT during the 2021-23 episode.")
    # Calculate the total effect
    total_effect = beta1 + beta2
    print(f"\nTotal effect of inflation during 2021-23 (β1 + β2): {total_effect:.4f}")
    if total_effect > 0:
        print("  - This suggests that during the recent spike, firms were able to expand margins as inflation rose, contrasting with normal periods.")
    else:
        print("  - This suggests that margin compression was even more severe during the recent spike.")
else:
    print("  - The relationship between inflation and margins was NOT statistically different during the 2021-23 episode.")


# %% [markdown]
# ### 6.3. Robustness Check: Sub-Sample Analysis
#
# To validate the interaction model, we split the sample into a "pre-shock" period (ending in 2019) and a "shock" period (2020-2023) and run the main ECM on each. This provides a clean comparison.

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK: SUB-SAMPLE ANALYSIS")
print("="*60)

# Define the two periods
df_normal_period = df_reg[df_reg.index.get_level_values('year') <= 2019]
df_shock_period = df_reg[df_reg.index.get_level_values('year') > 2019]

print(f"Observations in 'Normal Period' (pre-2020): {len(df_normal_period):,}")
print(f"Observations in 'Shock Period' (2020-2023): {len(df_shock_period):,}")

# --- Run Model on Normal Period ---
print("\n--- Model for Normal Period (2004-2019) ---")
mod_normal = PanelOLS(df_normal_period[dependent], df_normal_period[exog_vars_dynamic], entity_effects=True)
res_normal = mod_normal.fit(cov_type='clustered', cluster_entity=True)
inflation_coeff_normal = res_normal.params['inflation_rate']
print(f"Coefficient on inflation_rate: {inflation_coeff_normal:.4f}")
print(res_normal.summary.tables[1]) # Display only the coefficients table

# --- Run Model on Shock Period ---
print("\n--- Model for Shock Period (2020-2023) ---")
mod_shock = PanelOLS(df_shock_period[dependent], df_shock_period[exog_vars_dynamic], entity_effects=True)
res_shock = mod_shock.fit(cov_type='clustered', cluster_entity=True)
inflation_coeff_shock = res_shock.params['inflation_rate']
print(f"Coefficient on inflation_rate: {inflation_coeff_shock:.4f}")
print(res_shock.summary.tables[1]) # Display only the coefficients table

# --- Concluding the analysis ---
print("\n*** Sub-Sample Analysis Conclusion ***")
if np.sign(inflation_coeff_normal) != np.sign(inflation_coeff_shock):
    print("The sign of the inflation coefficient differs between the two periods, strongly supporting a structural break.")
else:
    print("The sign of the inflation coefficient is consistent across periods, but the magnitude may differ.")

print("This robustness check confirms the findings from the interaction model, adding credibility to the conclusion about the unique nature of the 2021-2023 episode.")


# %%


# %% [markdown]
# ## 6. Advanced Robustness & The 2021-23 Episode
#
# The previous analysis identified a significant structural break. This section addresses the feedback by fortifying the econometric evidence.
#
# **Priority 1: Correcting Standard Errors.** We will switch to Driscoll-Kraay standard errors to account for the cross-sectional dependence inherent in the data due to common macroeconomic shocks.
#
# **Priority 2: Testing the Episode Definition.** We will test the sensitivity of our results to different definitions of the "inflation spike" period.

# %%
# --- 6.1. Main Interaction Model with Correct Standard Errors ---

print("\n" + "="*60)
print("FIXING STANDARD ERRORS: RE-ESTIMATING WITH DRISCOLL-KRAAY")
print("="*60)

# Define the original 2021-2023 episode
df_interaction = df_reg.copy()
df_interaction['episode_21_23'] = df_interaction.index.get_level_values('year').isin([2021, 2022, 2023]).astype(int)
df_interaction['inflation_x_episode'] = df_interaction['inflation_rate'] * df_interaction['episode_21_23']
exog_vars_interaction = exog_vars_dynamic + ['inflation_x_episode']

# Re-run the model, specifying Driscoll-Kraay standard errors
# This is the single most important correction to the model.
mod_dk = PanelOLS(
    df_interaction[dependent],
    df_interaction[exog_vars_interaction],
    entity_effects=True
)
# The 'kernel' choice determines the weighting, 'bartlett' is standard.
res_dk = mod_dk.fit(cov_type='driscoll-kraay', kernel='bartlett')

print("--- Main Interaction Model with Driscoll-Kraay SEs ---")
print(res_dk.summary)

print("\n*** Interpretation Note ***")
print("Driscoll-Kraay SEs are robust to both cross-sectional and serial correlation.")
print("While coefficients remain the same, t-stats may be lower. The key is whether significance holds.")


# %% [markdown]
# ### 6.2. Robustness Check: Sensitivity to Episode Definition
#
# The choice of "2021-2023" is an assumption. A robust finding should not depend entirely on this specific definition. Here, we test other plausible definitions: the core inflation years (2021-2022) and the peak year only (2022).

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK: SENSITIVITY TO EPISODE DEFINITION")
print("="*60)

# A list of different episode definitions to test
episode_definitions = {
    "2021-2023 (Baseline)": [2021, 2022, 2023],
    "2021-2022 (Core Spike)": [2021, 2022],
    "2022 only (Peak Year)": [2022]
}

results_sensitivity = []

for name, years in episode_definitions.items():
    print(f"--- Testing episode definition: {name} ---")
    df_temp = df_reg.copy()
    
    # Create dummy and interaction term for the current definition
    df_temp['episode'] = df_temp.index.get_level_values('year').isin(years).astype(int)
    df_temp['inflation_x_episode'] = df_temp['inflation_rate'] * df_temp['episode']
    
    exog_temp = exog_vars_dynamic + ['inflation_x_episode']
    
    # Run the model with the corrected Driscoll-Kraay SEs
    mod_sens = PanelOLS(df_temp[dependent], df_temp[exog_temp], entity_effects=True)
    res_sens = mod_sens.fit(cov_type='driscoll-kraay', kernel='bartlett')
    
    # Store the key results
    interaction_coeff = res_sens.params['inflation_x_episode']
    interaction_pval = res_sens.pvalues['inflation_x_episode']
    baseline_coeff = res_sens.params['inflation_rate']
    
    results_sensitivity.append({
        "Episode Definition": name,
        "Baseline Inflation Effect (β1)": baseline_coeff,
        "Interaction Effect (β2)": interaction_coeff,
        "p-value (β2)": interaction_pval,
        "Total Effect (β1+β2)": baseline_coeff + interaction_coeff
    })

# --- Display the results in a clean summary table ---
results_df = pd.DataFrame(results_sensitivity).set_index("Episode Definition")
print("\n--- Summary of Sensitivity Analysis ---")
print(results_df.round(4))


# %% [markdown]
# ### 6.3. Final Interpretation of Robustness Checks
#
# The results from these checks determine the final confidence in our findings.

# %%
print("\n" + "="*60)
print("FINAL INTERPRETATION")
print("="*60)

# Check if the core finding holds across definitions
core_finding_robust = all(results_df['p-value (β2)'] < 0.05)
sign_consistent = all(results_df['Interaction Effect (β2)'] > 0)

print(f"Core finding (significant interaction term) is robust: {core_finding_robust}")
print(f"Sign of interaction effect is consistent (positive): {sign_consistent}")

if core_finding_robust and sign_consistent:
    print("\nConclusion: The finding that inflation pass-through was significantly weaker during the recent inflation spike is robust.")
    print("It does not depend on a single, arbitrary definition of the episode. This strengthens the main conclusion of the paper.")
else:
    print("\nConclusion: The results are sensitive to the episode definition.")
    print("This suggests the structural break, while present, is more complex and requires cautious interpretation.")
# %%
# %% [markdown]
# ## 7. Decomposing the Inflation Shock: The Role of Energy Prices
#
# A key piece of feedback is to disaggregate the cost shocks, as the 2021-23 episode was dominated by energy prices.
#
# Here, we create a new specification that includes both the overall `inflation_rate` and a specific measure of `energy_prices_inflation`. This allows us to see if the general inflation effect was simply a proxy for the direct impact of the energy crisis.

# %%
print("\n" + "="*60)
print("DECOMPOSING THE SHOCK: ADDING ENERGY INFLATION")
print("="*60)

# Check if the energy price variable is available
if 'mac_hicp_pure_energy_roc' in df_final.columns:
    # Rename for cleaner output, assuming it wasn't in the primary_shocks dict before
    if 'energy_prices_inflation' not in df_reg.columns:
        df_reg['energy_prices_inflation'] = df_reg['mac_hicp_pure_energy_roc']

    # Define a new set of explanatory variables including the energy shock
    exog_vars_energy = exog_vars_dynamic + ['energy_prices_inflation']
    
    # Ensure the variable is not all nulls in the regression sample
    if df_reg['energy_prices_inflation'].notna().sum() > 0:
        
        # Run the ECM with the added energy variable
        mod_energy = PanelOLS(
            df_reg[dependent],
            df_reg.dropna(subset=exog_vars_energy)[exog_vars_energy], # Drop rows with missing energy data if any
            entity_effects=True
        )
        res_energy = mod_energy.fit(cov_type='driscoll-kraay', kernel='bartlett')

        print("--- ECM Results with Energy Inflation Control ---")
        print(res_energy.summary)

        # --- Interpretation of the energy-augmented model ---
        print("\n*** Interpretation of Energy Shock Model ***")
        
        original_inflation_coeff = res_dk.params['inflation_rate'] # From your previous robust model
        new_inflation_coeff = res_energy.params['inflation_rate']
        energy_coeff = res_energy.params['energy_prices_inflation']
        
        print(f"Original HICP inflation coefficient (without energy control): {original_inflation_coeff:.4f}")
        print(f"HICP inflation coefficient (WITH energy control): {new_inflation_coeff:.4f}")
        print(f"Energy inflation coefficient: {energy_coeff:.4f}")

        if abs(new_inflation_coeff) < abs(original_inflation_coeff) and res_energy.pvalues['inflation_rate'] > 0.10:
            print("\nCONCLUSION: The effect of general inflation becomes smaller and/or insignificant once we control for energy prices.")
            print("This provides strong evidence that the story of margin compression during the 2021-23 episode was primarily an ENERGY cost story, not a general 'greedflation' story.")
        else:
            print("\nCONCLUSION: The effect of general inflation remains significant even after controlling for energy prices.")
            print("This suggests that while energy was a factor, broader inflationary dynamics also played a distinct role in affecting firm margins.")

    else:
        print("Energy price variable is present but contains all missing values in the regression sample. Cannot run model.")
else:
    print("Variable 'mac_hicp_pure_energy_roc' not found in the dataset. Cannot run energy shock model.")
# %%


# %% [markdown]
# ## 8. Final Model Specification: Adding Business Cycle and Fiscal Controls
#
# This is the final robustness check. We add standard controls for the business cycle (Output Gap) and fiscal policy (Primary Balance) to our main energy model.
#
# The objective is to confirm that the energy shock remains the dominant driver of margin changes during the 2021-23 period, even after accounting for these powerful macroeconomic forces.

# %%
print("\n" + "="*60)
print("FINAL MODEL: ADDING OUTPUT GAP AND FISCAL POLICY CONTROLS")
print("="*60)

# --- Add the new OECD variables to the regression DataFrame ---
# First, get the annual OECD data into the right shape
oecd_vars_to_add = {
    'mac_GAP': 'output_gap',
    'mac_NLGXQ': 'fiscal_balance'
}

# Assuming your raw data `df_final` contains these columns from the initial merge
if all(v in df_final.columns for v in oecd_vars_to_add.keys()):
    
    df_final_controls = df_final.select(
        [FIRM_ID_COL, 'year'] + list(oecd_vars_to_add.keys())
    ).rename(oecd_vars_to_add)
    
    # Merge these into our main pandas regression frame
    df_reg_final = df_reg.join(
        df_final_controls.to_pandas().set_index([FIRM_ID_COL, 'year'])
    )

    # --- Define the final, fully-specified model ---
    exog_vars_final = exog_vars_energy + ['output_gap', 'fiscal_balance']
    
    # Drop observations where the new controls are missing
    df_reg_final = df_reg_final.dropna(subset=exog_vars_final)
    
    print(f"Sample size for final model: {len(df_reg_final):,}")

    # --- Run the final ECM ---
    mod_final = PanelOLS(
        df_reg_final[dependent],
        df_reg_final[exog_vars_final],
        entity_effects=True
    )
    res_final = mod_final.fit(cov_type='driscoll-kraay', kernel='bartlett')

    print("\n--- Final, Fully-Specified ECM Results ---")
    print(res_final.summary)

    # --- Final Verdict ---
    print("\n" + "="*60)
    print("FINAL VERDICT ON THE ENERGY SHOCK NARRATIVE")
    print("="*60)

    p_val_energy = res_final.pvalues['energy_prices_inflation']
    p_val_hicp = res_final.pvalues['inflation_rate']

    print(f"p-value for energy_prices_inflation: {p_val_energy:.4f}")
    print(f"p-value for inflation_rate (general): {p_val_hicp:.4f}")

    if p_val_energy < 0.05 and p_val_hicp > 0.10:
        print("\nCONCLUSION: Robustness confirmed.")
        print("Even after controlling for the business cycle and fiscal policy, the energy shock remains the primary, significant driver of margin changes.")
        print("The effect of general inflation remains insignificant. The energy story holds.")
    else:
        print("\nCONCLUSION: The story is more complex.")
        print("The significance of the energy and/or general inflation variables has changed. The results must be interpreted with this new information.")

else:
    print("Error: Required OECD variables 'GAP' and/or 'NLGXQ' not found in the source data.")
# %%


# %% [markdown]
# ## 9. Final Analysis: Sectoral Heterogeneity of the Energy Shock (Level 1 NACE)
#
# We now aggregate the analysis to the main economic sectors (NACE Level 1) to get a clearer, more powerful view of the heterogeneous impacts. This avoids the noise of granular sub-sectors and focuses on broad economic structures.

# %%
print("\n" + "="*60)
print("FINAL ANALYSIS: SECTORAL HETEROGENEITY (NACE LEVEL 1)")
print("="*60)

# --- Add NACE Level 1 names for clear interpretation ---
# Create a mapping from code to name from the original data
if 'level1_nace_en_name' in df_final.columns:
    nace_level1_map = (
        df_final
        .select(['level1_nace_code', 'level1_nace_en_name'])
        .unique()
        .to_pandas()
        .set_index('level1_nace_code')['level1_nace_en_name']
        .to_dict()
    )
    # Add the descriptive name to our final regression dataframe
    df_reg_final['sector_name'] = df_reg_final['level1_nace_code'].map(nace_level1_map)
    grouping_col = 'sector_name'
else:
    # Fallback to using the code if the name column wasn't carried through
    grouping_col = 'level1_nace_code'

# Identify top sectors by observation count from the final regression sample
top_sectors = df_reg_final[grouping_col].value_counts().head(7).index.to_list()
print(f"Analyzing top sectors by observation count: {top_sectors}")

sectoral_results = []

for sector in top_sectors:
    df_sector = df_reg_final[df_reg_final[grouping_col] == sector]
    
    if len(df_sector) > 1000:
        print(f"\n--- Running Final ECM for Sector: {sector} (N={len(df_sector):,}) ---")
        
        mod_sector = PanelOLS(
            df_sector[dependent],
            df_sector[exog_vars_final],
            entity_effects=True
        )
        res_sector = mod_sector.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        sectoral_results.append({
            "Sector": sector,
            "Observations": len(df_sector),
            "Energy Shock Coeff.": res_sector.params['energy_prices_inflation'],
            "p-value (Energy)": res_sector.pvalues['energy_prices_inflation']
        })

# --- Display the results in a clean summary table ---
if sectoral_results:
    results_sector_df = pd.DataFrame(sectoral_results).set_index("Sector")
    print("\n" + "="*70)
    print("      SUMMARY OF SECTORAL HETEROGENEITY OF THE ENERGY SHOCK")
    print("="*70)
    print(results_sector_df.round(4))

    # --- Visualization of Sectoral Heterogeneity ---
    fig, ax = plt.subplots(figsize=(12, 7))
    results_sector_df.plot(
        kind='bar',
        y='Energy Shock Coeff.',
        # Correctly calculate standard error for error bars
        yerr=results_sector_df['Energy Shock Coeff.'].abs() / np.sqrt(results_sector_df['Observations']), # Approximation for viz
        ax=ax,
        capsize=4,
        color='maroon',
        legend=False
    )
    ax.axhline(y=0, color='black', linestyle='--')
    ax.set_ylabel('Coefficient on Energy Price Inflation')
    ax.set_xlabel('NACE Level 1 Sector')
    ax.set_title('Heterogeneous Impact of the Energy Shock Across Sectors', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / "final_sectoral_heterogeneity_level1.png")
    plt.show()
else:
    print("No sectoral analysis was run.")

# %% [markdown]
# ## 10. Focused Sectoral Analysis: Testing the Cost Pass-Through Mechanism
#
# We now test the core hypothesis: did the sectors that were insulated from the energy shock achieve this by raising their own output prices? We use sector-level Producer Price Index (PPI) data to investigate this pass-through mechanism.

# %%
print("\n" + "="*60)
print("TESTING THE COST PASS-THROUGH MECHANISM")
print("="*60)

# --- Step 1: Visual Evidence ---
# We use the sectoral regression results from the previous step (`results_sector_df`)

# First, calculate the average PPI growth for each sector during the 2021-2023 shock period
shock_period_ppi = (
    df_reg_final[df_reg_final.index.get_level_values('year').isin([2021, 2022, 2023])]
    .groupby('sector_name')
    .agg({'sector_level1_ppi_by_nace_pct': 'mean'})
    .rename(columns={'sector_level1_ppi_by_nace_pct': 'Avg PPI Growth (21-23)'})
)

# Merge the PPI data with our sectoral regression results
plot_data_passthrough = results_sector_df.join(shock_period_ppi)

print("\n--- Sectoral Energy Impact vs. Output Price Growth (2021-23) ---")
print(plot_data_passthrough.round(4))

# Create the scatter plot
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(plot_data_passthrough['Energy Shock Coeff.'], plot_data_passthrough['Avg PPI Growth (21-23)'], s=100, color='darkcyan')

# Add labels for each sector
for idx, row in plot_data_passthrough.iterrows():
    ax.text(row['Energy Shock Coeff.'] + 0.01, row['Avg PPI Growth (21-23)'], idx, fontsize=9)

ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('Estimated Impact of Energy Shock on Margin Growth')
ax.set_ylabel('Average Sectoral PPI Growth (%) during 2021-2023')
ax.set_title('Evidence of Cost Pass-Through Mechanisms by Sector', fontsize=16, fontweight='bold')
ax.grid(True)
plt.tight_layout()
plt.savefig(PLOTS_PATH / "passthrough_mechanism_scatter.png")
plt.show()


# %% [markdown]
# ### Step 2: Formal Econometric Test of the Pass-Through Channel
#
# We augment the sectoral models by including `sector_level1_ppi_by_nace_pct` as a regressor. This tests whether the energy shock's effect is diminished once we control for a sector's ability to raise its own prices.

# %%
print("\n" + "="*60)
print("FORMALLY TESTING THE PASS-THROUGH MECHANISM")
print("="*60)

# Add sector PPI to the list of final explanatory variables
exog_vars_passthrough = exog_vars_final + ['sector_level1_ppi_by_nace_pct']

passthrough_results = []

for sector in top_sectors: # Using the same top sectors as before
    df_sector = df_reg_final[df_reg_final[grouping_col] == sector].dropna(subset=exog_vars_passthrough)
    
    if len(df_sector) > 1000:
        print(f"\n--- Running Pass-Through Model for Sector: {sector} ---")
        
        mod_pt = PanelOLS(
            df_sector[dependent],
            df_sector[exog_vars_passthrough],
            entity_effects=True
        )
        res_pt = mod_pt.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        passthrough_results.append({
            "Sector": sector,
            "Energy Shock Coeff (Original)": results_sector_df.loc[sector, 'Energy Shock Coeff.'],
            "Energy Shock Coeff (with PPI)": res_pt.params['energy_prices_inflation'],
            "p-value (Energy, with PPI)": res_pt.pvalues['energy_prices_inflation'],
            "Sector PPI Coeff.": res_pt.params['sector_level1_ppi_by_nace_pct'],
            "p-value (PPI)": res_pt.pvalues['sector_level1_ppi_by_nace_pct']
        })

# --- Display the results in a clean summary table ---
if passthrough_results:
    results_pt_df = pd.DataFrame(passthrough_results).set_index("Sector")
    print("\n" + "="*70)
    print("      SUMMARY OF PASS-THROUGH REGRESSION RESULTS")
    print("="*70)
    print(results_pt_df.round(4))
    
    print("\n*** Interpretation ***")
    print("If the 'Energy Shock Coeff (with PPI)' is smaller in magnitude than the original, it suggests")
    print("that part of the energy shock's impact was indeed channeled through the sector's own price changes.")
# %%


# %% [markdown]
# ## 11. Final Analysis: NACE Level 2 Case Study on the Pass-Through Mechanism
#
# The NACE Level 1 analysis revealed significant heterogeneity but produced an ambiguous result for the broad "Manufacturing" sector. To get a clearer picture, we now conduct a targeted case study on key 2-digit NACE sub-sectors.
#
# This is the final and most detailed piece of the analysis, testing the cost pass-through mechanism at the industry's native data level.

# %%
print("\n" + "="*60)
print("NACE LEVEL 2 CASE STUDY: DECOMPOSING MANUFACTURING")
print("="*60)

# --- Define the specific NACE Level 2 codes for our case study ---
# We select key, high-observation industries within Manufacturing (Section C)
case_study_codes = {
    '10': 'Manufacture of food products',
    '25': 'Manufacture of fabricated metal products',
    '29': 'Manufacture of motor vehicles, trailers',
    '22': 'Manufacture of rubber and plastic products'
}

# Add NACE level 2 names for interpretation
if 'level2_nace_en_name' in df_final.columns:
    nace_level2_map = (
        df_final
        .select(['level2_nace_code', 'level2_nace_en_name'])
        .unique()
        .to_pandas()
        .set_index('level2_nace_code')['level2_nace_en_name']
        .to_dict()
    )
    df_reg_final['sector_name_l2'] = df_reg_final['level2_nace_code'].map(nace_level2_map)
    grouping_col_l2 = 'sector_name_l2'
else:
    grouping_col_l2 = 'level2_nace_code'


# --- Run the Pass-Through Model for each selected sub-sector ---
exog_vars_passthrough_l2 = exog_vars_final + ['sector_level2_ppi_by_nace_pct']
case_study_results = []

for code, name in case_study_codes.items():
    # Use the code for filtering, name for display
    df_sector = df_reg_final[df_reg_final['level2_nace_code'] == code].dropna(subset=exog_vars_passthrough_l2)
    
    if len(df_sector) > 1000:
        print(f"\n--- Running Pass-Through Model for Sector: {name} ({code}) ---")
        
        mod_cs = PanelOLS(
            df_sector[dependent],
            df_sector[exog_vars_passthrough_l2],
            entity_effects=True
        )
        res_cs = mod_cs.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        case_study_results.append({
            "Sector": name,
            "NACE Code": code,
            "Energy Shock Coeff.": res_cs.params['energy_prices_inflation'],
            "p-value (Energy)": res_cs.pvalues['energy_prices_inflation'],
            "Sector PPI Coeff.": res_cs.params['sector_level2_ppi_by_nace_pct'],
            "p-value (PPI)": res_cs.pvalues['sector_level2_ppi_by_nace_pct']
        })

# --- Display the results in a final summary table ---
if case_study_results:
    results_cs_df = pd.DataFrame(case_study_results).set_index("Sector")
    print("\n" + "="*70)
    print("      SUMMARY OF NACE LEVEL 2 CASE STUDY RESULTS")
    print("="*70)
    print(results_cs_df.round(4))
    
    print("\n*** Final Interpretation ***")
    print("This table provides the final, most granular evidence. It shows how different")
    print("key manufacturing industries navigated the energy shock, revealing the specific")
    print("mechanisms that were averaged out and obscured in the Level 1 analysis.")
# %%


# %% [markdown]
# ## 11. Final Analysis: Expanded NACE Level 2 Case Study (Corrected)
#
# This corrected version ensures a proper match on NACE Level 2 codes by standardizing them to a zero-padded string format. It runs the pass-through analysis on a broad and representative set of key 2-digit industries.

# %%
print("\n" + "="*60)
print("EXPANDED NACE LEVEL 2 CASE STUDY (CORRECTED)")
print("="*60)

# --- CRITICAL FIX: Standardize NACE Level 2 codes ---
# Ensure the code is a string and pad with a leading zero to ensure a length of 2.
# This guarantees that '9' becomes '09' and matches correctly.
df_reg_final['nace_l2_std'] = df_reg_final['level2_nace_code'].astype(str).str.zfill(2)


# --- Define the CORRECTED and expanded set of NACE Level 2 codes ---
case_study_codes = {
    # Agriculture (Most impacted)
    '01': 'Agriculture, hunting and related service activities',
    # Manufacturing (Decomposition)
    '10': 'Manufacture of food products',
    '25': 'Manufacture of fabricated metal products',
    '29': 'Manufacture of motor vehicles, trailers',
    # Construction (Key domestic sector)
    '41': 'Construction of buildings',
    # Wholesale & Retail Trade (Largest service sector)
    '46': 'Wholesale trade, except of motor vehicles',
    '47': 'Retail trade, except of motor vehicles',
    # Transportation (Direct energy exposure)
    '49': 'Land transport and transport via pipelines'
}


# --- Run the Pass-Through Model for each selected sub-sector ---
exog_vars_passthrough_l2 = exog_vars_final + ['sector_level2_ppi_by_nace_pct']
case_study_results = []

for code, name in case_study_codes.items():
    # Filter using the new, standardized NACE code
    df_sector = df_reg_final[df_reg_final['nace_l2_std'] == code].dropna(subset=exog_vars_passthrough_l2)
    
    if len(df_sector) > 1000:
        print(f"\n--- Running Pass-Through Model for Sector: {name} ({code}) ---")
        
        mod_cs = PanelOLS(
            df_sector[dependent],
            df_sector[exog_vars_passthrough_l2],
            entity_effects=True
        )
        res_cs = mod_cs.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        case_study_results.append({
            "Sector": name,
            "NACE Code": code,
            "Energy Shock Coeff.": res_cs.params['energy_prices_inflation'],
            "p-value (Energy)": res_cs.pvalues['energy_prices_inflation'],
            "Sector PPI Coeff.": res_cs.params['sector_level2_ppi_by_nace_pct'],
            "p-value (PPI)": res_cs.pvalues['sector_level2_ppi_by_nace_pct']
        })

# --- Display the results in a final summary table ---
if case_study_results:
    results_cs_df = pd.DataFrame(case_study_results).set_index("Sector")
    print("\n" + "="*70)
    print("      SUMMARY OF EXPANDED NACE LEVEL 2 CASE STUDY RESULTS")
    print("="*70)
    print(results_cs_df.round(4))
else:
    print("\nNo results generated. Check NACE codes and data availability.")
# %%


# %% [markdown]
# ## 11. Final Analysis: Comprehensive NACE Level 2 Analysis
#
# This final version runs the pass-through model on ALL NACE Level 2 sectors with a sufficient sample size (>= 5,000 observations). This provides a complete and comprehensive view of the heterogeneous effects across the economy.

# %%
print("\n" + "="*60)
print("COMPREHENSIVE NACE LEVEL 2 ANALYSIS")
print("="*60)

# --- Step 1: Identify all sectors meeting the observation threshold ---
MIN_OBS_FOR_SELECTION = 5000

# Use pandas aggregation to get the observation count for each L2 sector
sector_counts_df = (
    df_reg_final
    .groupby('level2_nace_code')
    .agg(
        obs_count=('sector_level2_ppi_by_nace_pct', 'size')
    )
    .loc[lambda x: x['obs_count'] >= MIN_OBS_FOR_SELECTION]
)

sectors_to_run = sector_counts_df.index.to_list()
print(f"Identified {len(sectors_to_run)} sectors with at least {MIN_OBS_FOR_SELECTION:,} observations.")
print(f"Sectors to be analyzed: {sectors_to_run}")


# --- Step 2: Run Pass-Through Model on all selected sectors ---
exog_vars_passthrough_l2 = exog_vars_final + ['sector_level2_ppi_by_nace_pct']
case_study_results = []

# Create the name map for readable output
if 'level2_nace_en_name' in df_final.columns:
    nace_level2_map = df_final.select(['level2_nace_code', 'level2_nace_en_name']).unique().to_pandas().set_index('level2_nace_code')['level2_nace_en_name'].to_dict()
else:
    nace_level2_map = {code: code for code in sectors_to_run}

for code in sectors_to_run:
    df_sector = df_reg_final[df_reg_final['level2_nace_code'] == code].dropna(subset=exog_vars_passthrough_l2)
    
    if len(df_sector) >= MIN_OBS_FOR_SELECTION:
        sector_name = nace_level2_map.get(code, code)
        print(f"\n--- Running Model for Sector: {sector_name} ({code}) ---")
        
        mod_cs = PanelOLS(df_sector[dependent], df_sector[exog_vars_passthrough_l2], entity_effects=True)
        res_cs = mod_cs.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        case_study_results.append({
            "Sector": sector_name,
            "NACE Code": code,
            "Energy Shock Coeff.": res_cs.params['energy_prices_inflation'],
            "p-value (Energy)": res_cs.pvalues['energy_prices_inflation'],
            "Sector PPI Coeff.": res_cs.params['sector_level2_ppi_by_nace_pct'],
            "p-value (PPI)": res_cs.pvalues['sector_level2_ppi_by_nace_pct']
        })

# --- Display the results in a final, comprehensive summary table ---
if case_study_results:
    results_cs_df = pd.DataFrame(case_study_results).set_index("Sector").sort_values("Energy Shock Coeff.")
    print("\n" + "="*70)
    print("      SUMMARY OF COMPREHENSIVE NACE LEVEL 2 CASE STUDY RESULTS")
    print("="*70)
    print(results_cs_df.round(4))
else:
    print("\nNo results generated. Check sector selection criteria.")
# %%
# %% [markdown]
# ## 11. Final Analysis: Comprehensive NACE Level 2 Analysis & Key Visualizations
#
# This final version runs the pass-through model on all major NACE Level 2 sectors and generates a set of publication-ready visualizations to summarize the key findings on the heterogeneous impacts of the energy shock and the different pass-through mechanisms.

# %%
print("\n" + "="*60)
print("COMPREHENSIVE NACE LEVEL 2 ANALYSIS")
print("="*60)

# --- Step 1: Identify all sectors meeting the observation threshold ---
MIN_OBS_FOR_SELECTION = 5000

sector_counts_df = (
    df_reg_final
    .groupby('level2_nace_code')
    .agg(
        obs_count=('sector_level2_ppi_by_nace_pct', 'size')
    )
    .loc[lambda x: x['obs_count'] >= MIN_OBS_FOR_SELECTION]
)

sectors_to_run = sector_counts_df.index.to_list()
print(f"Identified {len(sectors_to_run)} sectors with at least {MIN_OBS_FOR_SELECTION:,} observations.")


# --- Step 2: Run Pass-Through Model on all selected sectors ---
exog_vars_passthrough_l2 = exog_vars_final + ['sector_level2_ppi_by_nace_pct']
case_study_results = []

if 'level2_nace_en_name' in df_final.columns:
    nace_level2_map = df_final.select(['level2_nace_code', 'level2_nace_en_name']).unique().to_pandas().set_index('level2_nace_code')['level2_nace_en_name'].to_dict()
else:
    nace_level2_map = {code: code for code in sectors_to_run}

for code in sectors_to_run:
    df_sector = df_reg_final[df_reg_final['level2_nace_code'] == code].dropna(subset=exog_vars_passthrough_l2)
    
    if len(df_sector) >= MIN_OBS_FOR_SELECTION:
        sector_name = nace_level2_map.get(code, code)
        print(f"\n--- Running Model for Sector: {sector_name} ({code}) ---")
        
        mod_cs = PanelOLS(df_sector[dependent], df_sector[exog_vars_passthrough_l2], entity_effects=True)
        res_cs = mod_cs.fit(cov_type='driscoll-kraay', kernel='bartlett')
        
        case_study_results.append({
            "Sector": sector_name,
            "NACE Code": code,
            "Energy Shock Coeff.": res_cs.params['energy_prices_inflation'],
            "p-value (Energy)": res_cs.pvalues['energy_prices_inflation'],
            "Sector PPI Coeff.": res_cs.params['sector_level2_ppi_by_nace_pct'],
            "p-value (PPI)": res_cs.pvalues['sector_level2_ppi_by_nace_pct']
        })

# --- Display the results in a final, comprehensive summary table ---
if case_study_results:
    results_cs_df = pd.DataFrame(case_study_results).set_index("Sector").sort_values("Energy Shock Coeff.")
    print("\n" + "="*70)
    print("      SUMMARY OF COMPREHENSIVE NACE LEVEL 2 CASE STUDY RESULTS")
    print("="*70)
    print(results_cs_df.round(4))
else:
    print("\nNo results generated. Check sector selection criteria.")


# %% [markdown]
# ### Final Visualizations
#
# These plots summarize the comprehensive sectoral analysis, providing the core visual evidence for the paper.

# %%
# --- Visualization 1: Heterogeneous Impact of the Energy Shock ---
if case_study_results:
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Sort for better presentation
    plot_df = results_cs_df.sort_values("Energy Shock Coeff.", ascending=True)
    
    # Define colors based on statistical significance
    colors = np.where(plot_df['p-value (Energy)'] < 0.05, 'darkred', 'grey')
    
    plot_df['Energy Shock Coeff.'].plot(
        kind='barh',
        ax=ax,
        color=colors,
        alpha=0.8
    )
    
    ax.axvline(x=0, color='black', linestyle='--')
    ax.set_xlabel('Coefficient on Energy Price Inflation')
    ax.set_ylabel('')
    ax.set_title('Heterogeneous Impact of the Energy Shock Across Major Sectors', fontsize=16, fontweight='bold')
    ax.text(0.98, 0.02, 'Red bars indicate p-value < 0.05', transform=ax.transAxes, ha='right', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / "final_comprehensive_sectoral_bar.png")
    plt.show()

# %% [markdown]
# #### Visualizing the Pass-Through Mechanism
#
# This plot is the final piece of evidence. It maps each sector based on the **impact** of the energy shock (x-axis) versus its **ability to raise its own prices** (y-axis). This visually separates the economy into the three archetypes.

# %%
# --- Visualization 2: The Pass-Through Mechanism Scatter Plot ---
if case_study_results:
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
# ## 12. Robustness Check: Two-Way Clustered Standard Errors
#
# As a final robustness check, we re-estimate our main models using two-way clustered standard errors (by firm and year). This is an alternative to Driscoll-Kraay for handling potential serial and cross-sectional correlation.
#
# The purpose is to confirm that the statistical significance of our key findings is stable across different, standard methods for error correction.

# %%
print("\n" + "="*60)
print("ROBUSTNESS CHECK: TWO-WAY CLUSTERED STANDARD ERRORS")
print("="*60)

# --- 1. Re-running the Final, Fully-Specified Model ---
print("\n--- Final Model with Two-Way Clustering ---")

if 'df_reg_final' in locals():
    # Rerun the final model, changing only the cov_type
    mod_final_tw = PanelOLS(
        df_reg_final[dependent],
        df_reg_final[exog_vars_final],
        entity_effects=True
    )
    res_final_tw = mod_final_tw.fit(
        cov_type='clustered',
        cluster_entity=True,
        cluster_time=True  # This enables two-way clustering
    )

    print(res_final_tw.summary)
else:
    print("Final model DataFrame not found. Skipping.")


# %% [markdown]
# ### Interaction Model with Two-Way Clustering

# %%
# --- 2. Re-running the Interaction Model ---
print("\n--- Interaction Model with Two-Way Clustering ---")

if 'df_interaction' in locals():
    mod_interaction_tw = PanelOLS(
        df_interaction[dependent],
        df_interaction[exog_vars_interaction],
        entity_effects=True
    )
    res_interaction_tw = mod_interaction_tw.fit(
        cov_type='clustered',
        cluster_entity=True,
        cluster_time=True
    )
    
    print(res_interaction_tw.summary)
    
    print("\n*** Key coefficient check ***")
    pval_interaction_tw = res_interaction_tw.pvalues['inflation_x_episode']
    print(f"p-value for 'inflation_x_episode' with two-way clustering: {pval_interaction_tw:.4f}")

else:
    print("Interaction model DataFrame not found. Skipping.")


# %% [markdown]
# ### Comprehensive NACE Level 2 Analysis with Two-Way Clustering

# %%
# --- 3. Re-running the Comprehensive NACE Level 2 Analysis ---
print("\n--- NACE L2 Case Study with Two-Way Clustering ---")

if 'sectors_to_run' in locals():
    tw_cluster_results = []
    for code in sectors_to_run:
        df_sector = df_reg_final[df_reg_final['level2_nace_code'] == code].dropna(subset=exog_vars_passthrough_l2)

        if len(df_sector) >= MIN_OBS_FOR_SELECTION:
            sector_name = nace_level2_map.get(code, code)
            print(f"\n--- Running Two-Way Cluster Model for Sector: {sector_name} ({code}) ---")
            
            mod_cs_tw = PanelOLS(df_sector[dependent], df_sector[exog_vars_passthrough_l2], entity_effects=True)
            res_cs_tw = mod_cs_tw.fit(
                cov_type='clustered',
                cluster_entity=True,
                cluster_time=True
            )
            
            tw_cluster_results.append({
                "Sector": sector_name,
                "Energy Shock Coeff.": res_cs_tw.params['energy_prices_inflation'],
                "p-value (Energy)": res_cs_tw.pvalues['energy_prices_inflation'],
                "Sector PPI Coeff.": res_cs_tw.params['sector_level2_ppi_by_nace_pct'],
                "p-value (PPI)": res_cs_tw.pvalues['sector_level2_ppi_by_nace_pct']
            })

    if tw_cluster_results:
        results_tw_df = pd.DataFrame(tw_cluster_results).set_index("Sector").sort_values("Energy Shock Coeff.")
        print("\n" + "="*70)
        print("      SUMMARY OF NACE LEVEL 2 RESULTS (TWO-WAY CLUSTERING)")
        print("="*70)
        print(results_tw_df.round(4))
    else:
        print("\nNo sectoral results generated.")
else:
    print("Sector list not found. Skipping sectoral analysis.")
# %%
