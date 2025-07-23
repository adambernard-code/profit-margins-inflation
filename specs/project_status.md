# Project Status

*Last Updated: July 18, 2025*

This document provides a high-level overview of the current status of the "Profit Margins and Inflation" research project.

## Summary of Progress

The project is in the advanced stage of econometric analysis. All foundational data work is complete, and the merged panel dataset includes robust growth rate variables for firm, sector, and macro domains, as documented in the updated data inventory.

- **Completed Features:**
  - **Data Curation:** All primary data sources (MagnusWeb, CZSO, OECD, CNB, Eurostat) have been acquired, processed, and cleaned. Firm-level, sectoral, and macroeconomic variables are fully integrated.
  - **Data Quality:** The data quality pipeline is finalized, including robust outlier detection, per-year winsorisation of ratios, and aggressive winsorisation of growth variables. All transformations are reproducible and documented.
  - **Data Merging:** All curated datasets have been successfully merged into a single, analysis-ready panel dataset (`merged_panel_final.parquet`).
  - **Growth Rate Transformations:** Log year-over-year growth, percentage change, and difference in percentage points variables have been generated for all relevant domains. Documentation and inventory have been updated.
  - **Exploratory Analysis:** Comprehensive exploratory analysis completed in `00_exploratory_analysis_winsorized.ipynb`, covering descriptive statistics, time-series diagnostics, cross-sectional heterogeneity, panel persistence, bivariate relationships, multivariate structure (correlation/PCA), and outlier/influence checks. Data quality recommendations and cleaning rules have been formulated.
  - **Econometric Analysis:** The main panel analysis (`src_03_analysis/01_panel.py`) implements all core and advanced econometric models, including dynamic panel regressions, heterogeneity analysis, sector-level decomposition, event study, robustness checks (Driscoll-Kraay and two-way clustered SEs), pass-through mechanism tests, and macro-level causality analysis. All code is in sync with project specifications and reproducibility standards.

- **In-Progress Tasks:**
  - **Results Interpretation:** Analytical results are being interpreted in the context of the research questions and hypotheses. Final write-up of results and policy implications is underway.
  - **Final Plots and Tables:** Generation of publication-ready figures and tables for the thesis is ongoing.

- **Upcoming Milestones:**
  - Finalize all econometric models and robustness checks (including alternative outlier filters, if needed).
  - Complete all plots and tables for the final thesis.
  - Write the methodology and results chapters of the thesis.
  - Draft the final conclusion and policy recommendations.

## Component Status

This table tracks the status of the major components (Jupyter notebooks and scripts) in the project's workflow.

| Component / Notebook                               | Status        | Code Path                                                                                             |
| -------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| **Data Curation**                                  |               |                                                                                                       |
| `data_curation_magnusweb.ipynb`                    | ✅ Done       | [src_01_data_curation/data_curation_magnusweb.ipynb](../src_01_data_curation/data_curation_magnusweb.ipynb) |
| `data_curation_nace_data.ipynb`                    | ✅ Done       | [src_01_data_curation/data_curation_nace_data.ipynb](../src_01_data_curation/data_curation_nace_data.ipynb) |
| `data_curation_macro_indicators.ipynb`             | ✅ Done       | [src_01_data_curation/data_curation_macro_indicators.ipynb](../src_01_data_curation/data_curation_macro_indicators.ipynb) |
| `data_curation_import_prices.ipynb`                | ✅ Done       | [src_01_data_curation/data_curation_import_prices.ipynb](../src_01_data_curation/data_curation_import_prices.ipynb) |
| **Data Quality & Merging**                         |               |                                                                                                       |
| `01_magnusweb_dq.ipynb`                            | ✅ Done       | [src_02_data_quality/01_magnusweb_dq.ipynb](../src_02_data_quality/01_magnusweb_dq.ipynb) |
| `02_merge.ipynb`                                   | ✅ Done       | [src_02_data_quality/02_merge.ipynb](../src_02_data_quality/02_merge.ipynb) |
| `03_cal_growth.ipynb`                              | ✅ Done       | [src_02_data_quality/03_cal_growth.ipynb](../src_02_data_quality/03_cal_growth.ipynb) |
| **Analysis**                                       |               |                                                                                                       |
| `00_exploratory_analysis.ipynb`                    | ❌ Deprecated  | [src_03_analysis/00_exploratory_analysis.ipynb](../src_03_analysis/00_exploratory_analysis.ipynb) |
| `00_exploratory_analysis_winsorized.ipynb`         | ✅ Done        | [src_03_analysis/00_exploratory_analysis_winsorized.ipynb](../src_03_analysis/00_exploratory_analysis_winsorized.ipynb) |
| `01_panel.py`                                      | 🔄 In Progress (Advanced) | [src_03_analysis/01_panel.py](../src_03_analysis/01_panel.py) |
| `01_firm_level_panel.ipynb`                        | ❌ Deprecated  | [src_03_analysis/01_firm_level_panel.ipynb](../src_03_analysis/01_firm_level_panel.ipynb) |
| `02_sector_level_analysis.ipynb`                   | 🔄 In Progress | [src_03_analysis/02_sector_level_analysis.ipynb](../src_03_analysis/02_sector_level_analysis.ipynb) |
| `03_marco_analysis.ipynb`                          | ❌ Planned    | [src_03_analysis/03_marco_analysis.ipynb](../src_03_analysis/03_marco_analysis.ipynb) |

## Blocking Issues & Dependencies

*As of the last update, there are no major blocking issues. The primary dependency is the timely completion of the econometric analysis and final interpretation. All code is in sync with the latest specifications and data inventory. Outlier filtering rules and sector-specific cleaning recommendations from the exploratory analysis have been implemented in the main analysis script.*
