

# %% [markdown]
# # Exploratory Analysis for Chapter 3: Data and Descriptive Analysis
# 
# **Objective**: Generate the key visualizations and diagnostics for the data chapter. This notebook:
# 1.  Loads the final, winsorized firm-level panel dataset.
# 2.  Creates a time-series plot of aggregate median operating margins against HICP, core, and energy inflation.
# 3.  Generates an Autocorrelation Function (ACF) plot for the aggregate margin series to demonstrate persistence.
# 4.  Produces a correlation heatmap of the key macroeconomic variables (including core inflation) to check for multicollinearity.
# 5.  **New:** Creates plots from the original EDA to show firm tenure distribution, sectoral margin distributions (violin plots), and the rolling correlation between margins and inflation.
# 
# The outputs are saved to the `plots/` directory and are directly referenced in the LaTeX chapter.

# %%
# === Imports and Setup ===
import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.api as sm
import warnings
import sys

warnings.filterwarnings('ignore')

# --- Paths and Styling ---
DATA_PATH = Path("../data/data_ready/merged_panel_winsorized.parquet") 
PLOTS_PATH = Path("../plots/")


PLOTS_PATH.mkdir(exist_ok=True) 

# Enhanced plotting settings for publication quality
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")
print("Libraries imported and paths configured.")

# %% [markdown]
# ## Data Loading and Preparation
# 
# First, we define the manually-entered HICP series for core and energy inflation, sourced from the ECB Statistical Data Warehouse. Then, we load our main winsorized panel dataset and aggregate it to create the necessary time-series data for plotting.
# 
# **Note:** The script will now check if `merged_panel_winsorized.parquet` exists before proceeding.

# %%
# === Manually-Entered Inflation Data (ECB SDW) ===
core_inflation_dict = {
    1996: 14.7, 1997: 15.8, 1998: 18.2, 1999: 11.0, 2000: 3.5, 2001: 3.7, 2002: 1.3, 2003: 0.0, 2004: 2.4, 
    2005: 0.8, 2006: 0.8, 2007: 3.1, 2008: 5.4, 2009: 0.3, 2010: 0.7, 2011: 1.4, 2012: 2.8, 2013: 1.5, 
    2014: 1.1, 2015: 0.8, 2016: 1.2, 2017: 2.6, 2018: 1.8, 2019: 2.3, 2020: 3.9, 2021: 3.6, 2022: 12.5, 
    2023: 9.7, 2024: 2.7
}
energy_inflation_dict = {
    2001: 10.3, 2002: 1.9, 2003: -0.7, 2004: 3.7, 2005: 6.4, 2006: 9.7, 2007: 2.2, 2008: 11.0, 2009: 2.7,
    2010: 4.3, 2011: 7.2, 2012: 7.7, 2013: 0.6, 2014: -3.8, 2015: -3.0, 2016: -2.5, 2017: 1.2, 2018: 3.2,
    2019: 4.8, 2020: -1.5, 2021: 1.7, 2022: 31.5, 2023: 25.5, 2024: 3.0
}

# --- Check for data file before loading ---
if not DATA_PATH.is_file():
    print(f"--- ERROR ---")
    print(f"Data file not found at: '{DATA_PATH.resolve()}'")
    print("Please ensure the file 'merged_panel_winsorized.parquet' is in the same directory as this notebook.")
    # Stop execution if in a script context, or prevent further cells from running
    sys.exit("Execution stopped due to missing data file.") 
else:
    # --- Load and Process Data ---
    df = pl.read_parquet(DATA_PATH)

    # Aggregate firm-level data to get median operating margin per year
    agg_margins = df.group_by("year").agg(
        pl.col("firm_operating_margin_cal").median().alias("median_op_margin")
    ).sort("year").to_pandas()

    # Prepare inflation data
    inflation_df = pd.DataFrame({
        'year': list(core_inflation_dict.keys()),
        'core_inflation_rate': list(core_inflation_dict.values())
    }).merge(
        pd.DataFrame({
            'year': list(energy_inflation_dict.keys()),
            'energy_inflation_rate': list(energy_inflation_dict.values())
        }),
        on='year',
        how='outer'
    )

    # Get HICP data from the main dataframe
    hicp_df = df.select(["year", "mac_hicp_overall_roc"]).unique().sort("year").to_pandas()
    hicp_df.rename(columns={'mac_hicp_overall_roc': 'hicp_inflation_rate'}, inplace=True)

    # Merge all data for plotting
    plot_df = pd.merge(agg_margins, hicp_df, on='year')
    plot_df = pd.merge(plot_df, inflation_df, on='year')
    plot_df = plot_df[(plot_df['year'] >= 2003) & (plot_df['year'] <= 2023)]

    print("Data loaded and prepared for plotting.")
    display(plot_df.head())

# %% [markdown]
# ## Figure 3.1: Aggregate Margins vs. Inflation
# This plot visualizes the evolution of the median firm's operating margin against three key inflation indicators: headline HICP, core inflation (HICP excluding energy), and energy inflation.

# %%
# === Generate and Save Plot 1 ===
fig, ax1 = plt.subplots(figsize=(12, 7))

# Plotting the median operating margin
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Median Operating Margin (%)', color='black', fontsize=12)
ax1.plot(plot_df['year'], plot_df['median_op_margin'], color='black', marker='o', linestyle='-', label='Median Operating Margin')
ax1.tick_params(axis='y', labelcolor='black')

# Creating a second y-axis for inflation rates
ax2 = ax1.twinx()
ax2.set_ylabel('Year-on-Year Inflation (%)', color='gray', fontsize=12)
ax2.plot(plot_df['year'], plot_df['hicp_inflation_rate'], color='blue', marker='s', linestyle='--', label='HICP Inflation')
ax2.plot(plot_df['year'], plot_df['core_inflation_rate'], color='green', marker='^', linestyle=':', label='Core Inflation')
ax2.plot(plot_df['year'], plot_df['energy_inflation_rate'], color='red', marker='x', linestyle='-.', label='Energy Inflation')
ax2.tick_params(axis='y', labelcolor='gray')

# Final touches
fig.tight_layout()
plt.title('Aggregate Median Operating Margin and Inflation (2003–2023)', fontsize=16)
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9), fontsize=10)
plt.grid(True)

# Save the figure
plt.savefig(PLOTS_PATH / 'aggregate_margins_vs_inflation.png', dpi=300, bbox_inches='tight')
print(f"Plot saved to {PLOTS_PATH / 'aggregate_margins_vs_inflation.png'}")
plt.show()

# %% [markdown]
# ## Figure 3.2: Persistence of Profit Margins (ACF Plot)
# The Autocorrelation Function (ACF) plot visually demonstrates the persistence of profit margins by showing how the aggregate margin series is correlated with its own past values.

# %%
# === Generate and Save Plot 2 ===
acf_data = agg_margins.set_index('year')['median_op_margin'].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
sm.graphics.tsa.plot_acf(acf_data, lags=10, ax=ax, title="") # Remove default title
ax.set_title('Autocorrelation of Aggregate Median Operating Margin', fontsize=16)
ax.set_xlabel('Lag', fontsize=12)
ax.set_ylabel('Autocorrelation', fontsize=12)

# Save the figure
plt.savefig(PLOTS_PATH / 'acf_operating_margin.png', dpi=300, bbox_inches='tight')
print(f"Plot saved to {PLOTS_PATH / 'acf_operating_margin.png'}")
plt.show()

# %% [markdown]
# ## Figure 3.3: Macroeconomic Environment (Correlation Matrix)
# This heatmap displays the pairwise correlations between the key macroeconomic control variables, including core inflation, to identify potential multicollinearity issues.

# %%
# === Generate and Save Plot 3 ===
macro_vars = [
    'mac_hicp_overall_roc',
    'mac_hicp_pure_energy_roc',
    'mac_cnb_repo_rate_annual',
    'mac_GAP',
    'mac_NLGXQ',
    'mac_ULC',
    'mac_RPMGS'
]

# Extract unique macro data per year
macro_df = df.select(macro_vars + ['year']).unique().sort('year').to_pandas()

# Merge with core inflation data
macro_df = pd.merge(macro_df, inflation_df[['year', 'core_inflation_rate']], on='year', how='left')

# Rename for clarity in the plot
macro_df.rename(columns={
    'mac_hicp_overall_roc': 'HICP',
    'mac_hicp_pure_energy_roc': 'HICP (Energy)',
    'core_inflation_rate': 'Core Inflation',
    'mac_cnb_repo_rate_annual': 'CNB Repo Rate',
    'mac_GAP': 'Output Gap',
    'mac_NLGXQ': 'Primary Balance',
    'mac_ULC': 'Unit Labor Cost',
    'mac_RPMGS': 'Import Prices'
}, inplace=True)

# Ensure correct order for the heatmap
corr_cols = ['HICP', 'Core Inflation', 'HICP (Energy)', 'CNB Repo Rate', 'Output Gap', 'Primary Balance', 'Unit Labor Cost', 'Import Prices']
corr_matrix = macro_df[corr_cols].corr()

# Plotting the heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", annot_kws={"size": 10})
plt.title('Correlation Matrix of Key Macroeconomic Variables', fontsize=16)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save the figure
plt.savefig(PLOTS_PATH / 'macro_correlation_heatmap.png', dpi=300, bbox_inches='tight')
print(f"Plot saved to {PLOTS_PATH / 'macro_correlation_heatmap.png'}")
plt.show()

# %% [markdown]
# ## Additional Visualizations from EDA
# 
# This section includes code to generate the three additional plots recommended from the original exploratory data analysis notebook to further enrich the thesis chapter.

# %%
# === EDA Plot 1: Firm Tenure Distribution ===
print("Generating Firm Tenure Distribution plot...")
firm_tenure = df.group_by("firm_ico").agg(
    pl.count().alias("years_in_panel")
).to_pandas()

plt.figure(figsize=(12, 7))
sns.histplot(data=firm_tenure, x='years_in_panel', bins=21, kde=False)
plt.title('Distribution of Firm Tenure in Panel (2003-2023)', fontsize=16)
plt.xlabel('Number of Years in Panel')
plt.ylabel('Number of Firms')
plt.xticks(ticks=range(1, 22))
plt.grid(axis='y', alpha=0.5)
plt.tight_layout()
plt.savefig(PLOTS_PATH / 'firm_tenure_distribution.png', dpi=300)
print(f"Plot saved to {PLOTS_PATH / 'firm_tenure_distribution.png'}")
plt.show()

# %%
# === EDA Plot 2: Sectoral Margin Distributions (Violin Plots) ===
print("Generating Sectoral Margin Distribution violin plots...")
sentinel_years = [2019, 2020, 2021, 2022, 2023]
sector_df = df.filter(pl.col('year').is_in(sentinel_years)).select(
    ["year", "level1_nace_en_name", "firm_operating_margin_cal"]
).drop_nulls().to_pandas()

# Filter for major sectors to avoid clutter
major_sectors = sector_df['level1_nace_en_name'].value_counts().nlargest(8).index
sector_df_filtered = sector_df[sector_df['level1_nace_en_name'].isin(major_sectors)]

# Cap outliers for better visualization
sector_df_filtered['firm_operating_margin_cal'] = sector_df_filtered['firm_operating_margin_cal'].clip(-40, 40)

fig, axes = plt.subplots(len(sentinel_years), 1, figsize=(14, 20), sharex=True)
fig.suptitle('Operating Margin Distributions by Sector Across Sentinel Years', fontsize=18, y=1.02)

for i, year in enumerate(sentinel_years):
    ax = axes[i]
    year_data = sector_df_filtered[sector_df_filtered['year'] == year]
    sns.violinplot(ax=ax, data=year_data, x='level1_nace_en_name', y='firm_operating_margin_cal',
                   inner='quartile', scale='width', palette='viridis')
    ax.set_title(f'Year: {year}', fontsize=14)
    ax.set_ylabel('Operating Margin (%)')
    ax.set_xlabel('')
    ax.axhline(0, color='red', linestyle='--', alpha=0.7)
    # FIX: Removed the invalid 'ha' keyword. The 'rotation' argument is sufficient.
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(PLOTS_PATH / 'sectoral_margin_violins.png', dpi=300)
print(f"Plot saved to {PLOTS_PATH / 'sectoral_margin_violins.png'}")
plt.show()

# %%
# === EDA Plot 3: Rolling Correlation Analysis ===
print("Generating Rolling Correlation plot...")
rolling_corr_data = plot_df[['year', 'median_op_margin', 'hicp_inflation_rate']].copy()
rolling_corr_data.set_index('year', inplace=True)

# Calculate 5-year rolling correlations
rolling_corr_data['rolling_corr'] = rolling_corr_data['median_op_margin'].rolling(window=5).corr(rolling_corr_data['hicp_inflation_rate'])

plt.figure(figsize=(12, 7))
plt.plot(rolling_corr_data.index, rolling_corr_data['rolling_corr'], marker='o', linestyle='-', color='purple')
plt.axhline(0, color='black', linestyle='--', alpha=0.5)
plt.title('5-Year Rolling Correlation: Median Operating Margin and HICP Inflation', fontsize=16)
plt.xlabel('Year (End of Window)')
plt.ylabel('Correlation Coefficient')
plt.ylim(-1, 1)
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.savefig(PLOTS_PATH / 'rolling_correlation_margin_hicp.png', dpi=300)
print(f"Plot saved to {PLOTS_PATH / 'rolling_correlation_margin_hicp.png'}")
plt.show()