# Project Status

*Last Updated: July 16, 2025*

This document provides a high-level overview of the current status of the "Profit Margins and Inflation" research project.

## Summary of Progress

The project has made significant progress, moving from data acquisition and curation to the analysis phase. The foundational data work is largely complete, and the focus has now shifted to econometric modeling and interpretation.

- **Completed Features:**
  - **Data Curation:** All primary data sources (MagnusWeb, CZSO, OECD, CNB, Eurostat) have been acquired, processed, and cleaned. This includes firm-level financials, sectoral indicators, and macroeconomic variables.
  - **Data Quality:** Extensive data quality checks and enrichment have been performed on the core MagnusWeb firm-level dataset.
  - **Data Merging:** All curated datasets have been successfully merged into a single, analysis-ready panel dataset (`merged_panel_final.parquet`).
  - **Exploratory Analysis:** Initial exploratory data analysis has been completed to understand the characteristics of the dataset.

- **In-Progress Tasks:**
  - **Data Quality Checks:** Revisit the data quality checks of MagnusWeb - clean up the scripts and generate two or three datasets with different approaches and levels of cleaning.
  - **Econometric Analysis:** The core analytical work is in progress. This involves running panel data regressions to test the main research hypotheses.
  - **Results Interpretation:** Initial results from the models are being analyzed and interpreted in the context of the research questions.

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
| `data_curation_magnusweb.ipynb`                    | ✅ Done       | [src_01_data_curation/data_curation_magnusweb.ipynb](<../src_01_data_curation/data_curation_magnusweb.ipynb>) |
| `data_curation_nace_data.ipynb`                    | ✅ Done       | [src_01_data_curation/data_curation_nace_data.ipynb](<../src_01_data_curation/data_curation_nace_data.ipynb>) |
| `data_curation_macro_indicators.ipynb`             | ✅ Done       | [src_01_data_curation/data_curation_macro_indicators.ipynb](<../src_01_data_curation/data_curation_macro_indicators.ipynb>) |
| `data_curation_import_prices.ipynb`                | ✅ Done       | [src_01_data_curation/data_curation_import_prices.ipynb](<../src_01_data_curation/data_curation_import_prices.ipynb>) |
| **Data Quality & Merging**                         |               |                                                                                                       |
| `01_magnusweb_data_cleaning_enrichment.ipynb`      | ✅ Done       | [src_02_data_quality/01_magnusweb_data_cleaning_enrichment.ipynb](<../src_02_data_quality/01_magnusweb_data_cleaning_enrichment.ipynb>) |
| `02_magnusweb_dq.ipynb`                            | ✅ Done       | [src_02_data_quality/02_magnusweb_dq.ipynb](<../src_02_data_quality/02_magnusweb_dq.ipynb>)                   |
| `03_merge.ipynb`                                   | ✅ Done       | [src_02_data_quality/03_merge.ipynb](<../src_02_data_quality/03_merge.ipynb>)                               |
| **Analysis**                                       |               |                                                                                                       |
| `00_exploratory_analysis.ipynb`                    | 🔄 In Progress | [src_03_analysis/00_exploratory_analysis.ipynb](<../src_03_analysis/00_exploratory_analysis.ipynb>)       |
| `01_firm_level_panel.ipynb`                        | 🔄 In Progress | [src_03_analysis/01_firm_level_panel.ipynb](<../src_03_analysis/01_firm_level_panel.ipynb>)               |
| `02_sector_level_analysis.ipynb`                   | 🔄 In Progress | [src_03_analysis/02_sector_level_analysis.ipynb](<../src_03_analysis/02_sector_level_analysis.ipynb>)     |
| `03_marco_analysis.ipynb`                          | ❌ Planned    | [src_03_analysis/03_marco_analysis.ipynb](<../src_03_analysis/03_marco_analysis.ipynb>)                     |

## Blocking Issues & Dependencies

*As of the last update, there are no major blocking issues. The primary dependency is the timely completion of the econometric analysis to proceed with the final write-up.*
