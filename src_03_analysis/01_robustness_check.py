# %% [markdown]
# ## 16. Robustness Check: Specification Search for the Margin-Inflation Link
#
# This script systematically tests the stability of the correlation between profit margins and sectoral inflation. It runs a baseline "reverse-direction" panel model and then iteratively adds every available macro-economic control variable one by one to see if the core relationship is robust or spurious.

# %%
import pandas as pd
import polars as pl
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
import warnings

warnings.filterwarnings('ignore')

# --- Configuration ---
DATA_PATH = "../data/data_ready/merged_panel_winsorized.parquet"
FIRM_ID_COL = "firm_ico"
MIN_OBS_PER_SECTOR = 1000

# --- 1. Data Preparation ---
print("--- Preparing data for robustness check ---")

# Load and set up the panel index
df = pl.read_parquet(DATA_PATH).to_pandas().set_index([FIRM_ID_COL, 'year'])

# Define core variables for the reverse-direction model
dependent = 'sector_level2_ppi_by_nace_pct'
key_independent = 'firm_operating_margin_cal'

# Create lagged dependent for dynamics
df['l_sector_ppi'] = df.groupby(level=FIRM_ID_COL)[dependent].shift(1)

# List of ALL plausible macro controls to iterate through from your inventory
# We use the raw _dpp or _pct versions
potential_controls = [
    'mac_ULC_pct', 'mac_hicp_pure_energy_roc', 'mac_fx_czk_eur_annual_avg_pct',
    'mac_GAP_dpp', 'mac_NLGXQ_dpp', 'mac_RPMGS_pct', 'mac_UNR_dpp',
    'mac_PDTY_pct', 'mac_TTRADE_pct', 'mac_CPV_ANNPCT', 'mac_ITV_ANNPCT',
    'mac_cnb_repo_rate_annual_dpp'
]

# Base model includes the key independent variable and dynamics
base_exog = [key_independent, 'l_sector_ppi']

# --- 2. Iterative Regression Analysis ---
print(f"\n--- Running {len(potential_controls)} robustness regressions ---")

robustness_results = []

# Run the baseline model with no extra controls
try:
    df_base = df[base_exog + [dependent]].dropna()
    mod_base = PanelOLS(
        df_base[dependent],
        sm.add_constant(df_base[base_exog]),
        entity_effects=True,
        time_effects=True # Use time effects to absorb aggregate shocks
    )
    res_base = mod_base.fit(cov_type='clustered', cluster_entity=True)
    
    robustness_results.append({
        "Added Control": "None (Baseline)",
        "Margin Coeff.": res_base.params[key_independent],
        "p-value": res_base.pvalues[key_independent],
        "N Obs": res_base.nobs
    })
except Exception as e:
    print(f"Baseline model failed: {e}")


# Loop through each potential control variable
for control in potential_controls:
    print(f"  - Testing with control: {control}")
    
    current_exog = base_exog + [control]
    df_spec = df[current_exog + [dependent]].dropna()
    
    # Skip if the sample becomes too small
    if len(df_spec) < 10000:
        print(f"    - Skipping, insufficient observations.")
        continue
    
    try:
        mod_spec = PanelOLS(
            df_spec[dependent],
            sm.add_constant(df_spec[current_exog]),
            entity_effects=True,
            time_effects=True
        )
        res_spec = mod_spec.fit(cov_type='clustered', cluster_entity=True)
        
        robustness_results.append({
            "Added Control": control,
            "Margin Coeff.": res_spec.params[key_independent],
            "p-value": res_spec.pvalues[key_independent],
            "N Obs": res_spec.nobs
        })
    except Exception as e:
        # This will catch errors from collinearity, etc., and continue the loop
        print(f"    - Model failed for {control}: {e}")
        robustness_results.append({
            "Added Control": control,
            "Margin Coeff.": None,
            "p-value": None,
            "N Obs": len(df_spec)
        })

# --- 3. Summarize Results ---
if robustness_results:
    results_df = pd.DataFrame(robustness_results).set_index("Added Control")
    
    print("\n" + "="*70)
    print("      ROBUSTNESS OF MARGIN-INFLATION CORRELATION")
    print("="*70)
    print(results_df.round(4))
    
    print("\n*** Interpretation ***")
    print("This table shows how the estimated effect of profit margins on sectoral inflation")
    print("changes as different macroeconomic controls are added.")
    print("If the 'Margin Coeff.' remains stable in sign and significance across most specifications, the correlation is robust.")
    print("If it changes dramatically or loses significance, the correlation is fragile and likely spurious.")
else:
    print("\nNo regressions were successfully completed.")
# %%
