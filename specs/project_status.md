# Project Status

*Last Updated: July 18, 2025*

This document provides a high-level overview of the current status of the "Profit Margins and Inflation" research project.

## Summary of Progress

The project has transitioned from data acquisition and curation to advanced econometric analysis. All foundational data work is complete, and the merged panel dataset now includes robust growth rate variables for firm, sector, and macro domains, as documented in the updated data inventory.

- **Completed Features:**
  - **Data Curation:** All primary data sources (MagnusWeb, CZSO, OECD, CNB, Eurostat) have been acquired, processed, and cleaned. Firm-level, sectoral, and macroeconomic variables are fully integrated.
  - **Data Quality:** The data quality pipeline is finalized, including robust outlier detection, per-year winsorisation of ratios, and aggressive winsorisation of growth variables. All transformations are reproducible and documented.
  - **Data Merging:** All curated datasets have been successfully merged into a single, analysis-ready panel dataset (`merged_panel_final.parquet`).
  - **Growth Rate Transformations:** Log year-over-year growth, percentage change, and difference in percentage points variables have been generated for all relevant domains. Documentation and inventory have been updated.

- **In-Progress Tasks:**
  - **Exploratory Analysis:** Initial exploratory data analysis currently ongoing to identify trends and patterns in the data.
  - **Econometric Analysis:** Panel regression modeling is underway, using the enriched dataset. Model specifications and diagnostics are being iterated for validity and robustness.
  - **Results Interpretation:** Analytical results are being interpreted in the context of the research questions.

- **Upcoming Milestones:**
  - Finalize all econometric models and robustness checks.
  - Generate all plots and tables for the final thesis.
  - Write the methodology and results chapters of the thesis.
  - Draft the final conclusion and policy recommendations.

## Component Status

This table tracks the status of the major components (Jupyter notebooks) in the project's workflow.

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
| `00_exploratory_analysis.ipynb`                    | 🔄 In Progress | [src_03_analysis/00_exploratory_analysis.ipynb](../src_03_analysis/00_exploratory_analysis.ipynb) |
| `01_firm_level_panel.ipynb`                        | 🔄 In Progress | [src_03_analysis/01_firm_level_panel.ipynb](../src_03_analysis/01_firm_level_panel.ipynb) |
| `02_sector_level_analysis.ipynb`                   | 🔄 In Progress | [src_03_analysis/02_sector_level_analysis.ipynb](../src_03_analysis/02_sector_level_analysis.ipynb) |
| `03_marco_analysis.ipynb`                          | ❌ Planned    | [src_03_analysis/03_marco_analysis.ipynb](../src_03_analysis/03_marco_analysis.ipynb) |

## Blocking Issues & Dependencies

*As of the last update, there are no major blocking issues. The primary dependency is the timely completion of the econometric analysis to proceed with the final write-up.*
