# Project Specifications

*Last Updated: July 16, 2025*

This document outlines the technical specifications for the major modules and data products in the "Profit Margins and Inflation" project.

## 0. Data Inventory 'specs/data_inventory.json'

This file provides a structured inventory of all variables included in the merged panel dataset. The inventory is organized by variable categories, with each category grouping related variables (e.g., firm-level, sector-level, macroeconomic). For each variable, the following information is documented:

- **Variable Name:** The name of the variable as it appears in the dataset.
- **Description:** A brief explanation of what the variable represents.
- **Unit/Format:** The measurement unit or data type (e.g., numeric, string, percentage).
- **Source:** The original data source or module from which the variable was derived.

The inventory is based on the final merged dataset and is intended to facilitate data understanding, reproducibility, and analysis. Categories and variable details are derived from the merged_panel_inventory.csv file.

## 1. Data Curation Modules

The data curation process is structured as a series of Jupyter notebooks, each responsible for processing a specific data source.

### 1.1. `data_curation_magnusweb.ipynb`

- **Purpose:** To clean, process, and structure the raw firm-level financial data from MagnusWeb.
- **Input:** Raw MagnusWeb data exports (likely in CSV or Excel format).
- **Output:** A cleaned Parquet file (`magnusweb_panel_cleaned.parquet`) containing a tidy panel of firm-year financial data.
- **Data Models:**
    - **Input:** Wide-format table with one row per firm-year and columns for various financial metrics.
    - **Output:** Long-format (tidy) panel with columns for `firm_id`, `year`, `metric_name`, `metric_value`.
- **Acceptance Criteria:**
    - Output file is created in the `data/source_cleaned/` directory.
    - Data types are correct (e.g., numeric for financial values, integer for years).
    - No duplicate firm-year observations.
    - Key financial ratios (e.g., profit margin) are calculated and included.

### 1.2. `data_curation_nace_data.ipynb`

- **Purpose:** To process and harmonize sectoral data from the Czech Statistical Office (CZSO).
- **Input:** Raw CZSO data files (e.g., producer price indices, wage data).
- **Output:** A cleaned Parquet file (`data_by_nace_annual_tidy.parquet`) with sectoral indicators.
- **Data Models:**
    - **Input:** Various formats from CZSO.
    - **Output:** Tidy panel with `nace_code`, `year`, `indicator_name`, `indicator_value`.
- **Acceptance Criteria:**
    - NACE codes are standardized.
    - Time series are complete and consistently formatted.
    - Hierarchical propagation of data (`nace_data_propagation.ipynb`) is performed to fill gaps where appropriate.

### 1.3. `data_curation_macro_indicators.ipynb`

- **Purpose:** To collect and process macroeconomic indicators from various sources (OECD, CNB, Eurostat).
- **Input:** API calls or downloaded files from the respective institutions.
- **Output:** Cleaned Parquet files for each major indicator (e.g., `GDP_annual.parquet`, `hicp_overall_roc_annual.parquet`).
- **Acceptance Criteria:**
    - Data is consistently indexed by year.
    - Variable names are clear and standardized.

## 2. Data Merging and Final Dataset

### 2.1. `01_magnusweb_data_cleaning_enrichment.ipynb`
- **Purpose:** To perform initial cleaning and enrichment of the MagnusWeb data. Calculate key financial ratios and ensure data integrity.
- **Input:** Raw MagnusWeb data.
- **Output:** Cleaned Parquet file (`magnusweb_panel_with_margins.parquet`).

### 2.2. `01_magnusweb_dq.ipynb`
- **Purpose:** To perform comprehensive data quality checks on the MagnusWeb dataset, including time-series consistency, missingness, outlier detection, and duplicate handling.
- **Input:** Cleaned MagnusWeb data from previous enrichment step.
- **Output:** Quality-checked MagnusWeb data files saved in the `data/source_cleaned/` directory, specifically `magnusweb_panel_[version].parquet`.
- **Acceptance Criteria:**
    - Data quality checks (missingness, outliers, duplicates) are performed and logged.
    - Time-series consistency is verified for all key financial variables.
    - Winsorisation is applied to ratios.
    - Output files are free of duplicate firm-year keys and major data integrity issues.

### 2.3. `02_merge.ipynb`
- **Purpose:** To merge all curated data sources into a single, analysis-ready panel dataset.
- **Input:** All cleaned Parquet files from the `data/source_cleaned/` directory.
- **Output:** The final merged panel dataset (`merged_panel_final.parquet`).
- **Data Model (`merged_panel_final.parquet`):**
    - One row per firm-year.
    - Columns for:
        - `firm_ico` (unique firm identifier)
        - `year`
        - All firm-level financial variables.
        - All relevant sectoral indicators, matched by `level2_code` (NACE classification) and `year`.
        - All relevant macroeconomic indicators, matched by `year`.
- **Acceptance Criteria:**
    - The merge is successful without creating duplicate rows.
    - The final dataset contains the expected number of rows and columns.
    - An inventory of the final merged panel is created (`merged_panel_inventory.csv`).
    - Sector and macro columns are included and documented in the inventory.

### 2.4. `03_cal_growth.ipynb`
- **Purpose:** To generate growth rate variables (log year-over-year, percentage change, difference in percentage points) for all relevant firm, sector, and macro indicators in the merged panel.
- **Input:** Merged panel dataset (`merged_panel_final.parquet`).
- **Output:** Enriched panel dataset with new growth variables (`merged_panel_clean.parquet`), and a documentation file (`merged_panel_clean_growth_variables_docs.txt`).
- **Data Model:**
    - Adds columns for:
        - Log YoY growth (`_logyoy` suffix)
        - Percentage change (`_pct` suffix)
        - Difference in percentage points (`_dpp` suffix)
    - Growth variables are generated for all domains: firm, sector, macro.
- **Acceptance Criteria:**
    - All growth variables are calculated using robust, reproducible formulas.
    - Edge cases (e.g., zero denominators, non-positive values for logs) are handled explicitly.
    - Growth variable documentation is generated and includes all domains.
    - Data inventory is updated to reflect new growth variable categories.
    - No duplicate keys or data integrity issues are introduced.

## 3. Analysis Modules

### All those modules need to be revisited: 

### 3.1. `01_firm_level_panel.ipynb`

- **Purpose:** To conduct the primary firm-level econometric analysis.
- **Input:** `merged_panel_final.parquet`.
- **Output:** Regression results (tables), diagnostic plots, and summary statistics.
- **Methodology:**
    - Implement fixed effects panel regressions.
    - Control for firm, sector, and year fixed effects.
    - Test the relationship between profit margins and various cost and demand factors.
- **Acceptance Criteria:**
    - Regression models are statistically sound (e.g., pass tests for multicollinearity, heteroscedasticity).
    - Results are clearly presented and interpreted.
- **Next Steps:**
    - Implement dynamic panel models (e.g., Arellano-Bond) to address endogeneity.
    - Conduct event study analysis around key economic shocks.

### 3.2. `02_sector_level_analysis.ipynb`

- **Purpose:** To aggregate the data to the sector level and perform a similar analysis.
- **Input:** `merged_panel_final.parquet`.
- **Output:** Sector-level regression results and plots.
- **Acceptance Criteria:**
    - Aggregation is done correctly (e.g., using weighted averages).
    - Sector-level models are robust and well-specified.
- **Next Steps:**
    - Compare firm-level and sector-level results to identify aggregation effects.

### 3.3. `03_marco_analysis.ipynb`

- **Purpose:** To analyze the contribution of profit margins to overall inflation using a macroeconomic perspective.
- **Input:** `merged_panel_final.parquet` and aggregate inflation data.
- **Output:** Variance decomposition or Blinder-Oaxaca style decomposition results.
- **Acceptance Criteria:**
    - The decomposition method is correctly implemented.
    - The results quantify the contribution of margins vs. other factors to inflation.
- **Next Steps:**
    - This module is planned and has not been started yet. The immediate next step is to develop the theoretical framework for the decomposition.
