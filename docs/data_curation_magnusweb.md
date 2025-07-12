# Data Curation Script Documentation - MagnusWeb data 

This script transforms the raw MagnusWeb data (in CSV format) into a **wide firm-year panel** dataset, optimized for time-series and panel analysis (e.g., fixed-effects models). It leverages the **Polars** library for high-performance, memory-efficient processing via lazy evaluation. The final output is saved in the efficient Parquet format. This document outlines the main actions performed by the script, along with the rationale behind key data manipulations.

---

## Overview

The script performs the following major steps:

1. **Lazy Data Loading:**  
   - Scans all raw CSV files from the source directory using **Polars' lazy engine** (`scan_csv`), avoiding high memory usage.

2. **Wide-to-Long Transformation:**  
   - Separates static (firm-level metadata) columns from time-coded columns (e.g., `2023/4Q Aktiva celkem`).
   - **Melts** only the time-coded columns into a long (tidy) format, creating rows for each firm-period-metric observation.

3. **Column Parsing and Filtering:**  
   - Parses the melted column names to extract time-series information: **year**, **quarter**, and the **metric** name.
   - Filters the data to retain only **annual or 4th quarter (Q4)** observations, treating Q4 as the year-end snapshot.

4. **Pivoting to a Wide Panel:**  
   - **Pivots** the long-format data into a wide firm-year panel, where each row represents a unique firm-year combination and each metric (e.g., `profit_pre_tax`, `total_assets`) becomes a separate column.

5. **Data Cleaning and Standardization:**  
   - Renames columns to shorter, standardized English names.
   - Maps verbose Czech measure names to concise English slugs.
   - Converts columns to appropriate data types (e.g., categorical, integer, float) to optimize memory and performance.

6. **Static vs. Time-Series Columns:**
   - After constructing the wide panel, the script identifies columns that are static (do not change across years for each ICO) and columns that are time-variant (change across years for each ICO).
   - **Static columns:**
     - name, main_nace, main_nace_code, sub_nace_cz, sub_nace_cz_code, main_okec, main_okec_code, sub_okec, sub_okec_code, esa2010, esa95, locality, region, num_employees, num_employees_cat, turnover_cat, audit, consolidation, currency, date_founded, date_dissolved, status, legal_form, entity_type
   - **Time-series columns:**
     - year, costs, equity, profit_pre_tax, total_assets, turnover, total_liabilities, profit_net, oper_profit, sales_revenue
   - Static columns are removed before saving the final Parquet file, ensuring the output contains only time-variant columns relevant for econometric analysis.

7. **Saving the Final Dataset:**  
   - Saves the final wide panel as a Parquet file with Snappy compression, ensuring fast I/O for subsequent analysis.

---

## Detailed Actions and Rationale

### 1. Lazy Loading and Wide-to-Long Transformation

| **Action**             | **Description**                                                                                        | **Reasoning**                                                                                          |
|------------------------|--------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Lazy Scan & Concat** | Use `polars.scan_csv` to read multiple CSVs into a lazy DataFrame, then concatenate them.                | Minimizes memory usage by building an execution plan first, allowing Polars to optimize the entire workflow. |
| **Identify `id_cols`** | Select static (firm-level) columns such as "IČO", "Název subjektu", "Hlavní NACE", etc.                  | These columns serve as firm identifiers and are preserved during the melt operation.                    |
| **Melt `time_cols`**   | Use `melt()` to convert time-coded columns (e.g., `2022/4Q Náklady`) into a long format with `raw` and `val` columns. | A long format is an essential intermediate step for parsing time and metric information cleanly.         |

### 2. Column Parsing, Filtering, and Pivoting to Wide Panel

| **Action**             | **Description**                                                                                        | **Reasoning**                                                                                          |
|------------------------|--------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Parse Year/Quarter** | Use regex to extract the `year` and `quarter` from the raw melted column names.                        | Standardizes time information into distinct columns for filtering and aggregation.                     |
| **Filter for Year-End**| Keep only rows where the quarter is `4` or not specified (annual values).                              | Ensures that each firm has at most one observation per year, creating a consistent annual panel.       |
| **Pivot to Wide Panel**| Group the long data by `IČO` and `year`, then pivot the `metric` values into their own columns.          | Creates the final model-ready wide format (one row per firm-year), which is expected by most econometric packages. |
| **Attach Static Data** | Join the wide panel with the unique, static firm-level metadata.                                       | Enriches the panel with time-invariant firm characteristics like NACE codes, location, and founding date. |

### 3. Column Renaming and Measure Mapping

#### Column Renaming

| **Original Column Name**                       | **New Column Name**  | **Reasoning**                                              |
|------------------------------------------------|----------------------|------------------------------------------------------------|
| IČO, Název subjektu, Hlavní NACE, etc.           | ico, name, main_nace, etc. | Short, standardized names facilitate coding and analysis. |
| Datum vzniku, Datum zrušení                    | date_founded, date_dissolved | Provides clear, English names for key dates.             |

#### Measure Mapping

| **Original Measure Name**                          | **Mapped Name**       | **Reasoning**                                             | **Time-Series Variable** |
|---------------------------------------------------|-----------------------|-----------------------------------------------------------|-------------------------|
| Hospodářský výsledek před zdaněním                | profit_pre_tax        | Provides a concise, standard English name.                | Yes                    |
| Hospodářský výsledek za účetní období             | profit_net            | Clarifies that this is the net profit measure.            | Yes                    |
| Provozní hospodářský výsledek                     | oper_profit           | Shortens the metric name for operating profit.            | Yes                    |
| Náklady                                           | costs                 | Standard term used in English.                            | Yes                    |
| Obrat, Výnosy / Obrat Výnosy                      | sales_revenue         | Consolidates similar revenue measures under one term.     | Yes                    |
| Tržby, Výkony / Tržby Výkony                      | turnover              | Unifies turnover measures for consistency.                | Yes                    |
| Aktiva celkem                                     | total_assets          | Clearly indicates the total assets of the firm.           | Yes                    |
| Stálá aktiva                                      | fixed_assets          | Standard term for fixed assets.                           | No                     |
| Oběžná aktiva                                     | current_assets        | Indicates current assets.                                 | No                     |
| Ostatní aktiva                                    | other_assets          | Groups other asset categories under a unified term.       | No                     |
| Pasiva celkem                                     | total_liabilities     | Standardizes liabilities reporting.                       | Yes                    |
| Vlastní kapitál                                   | equity                | Short, standard term for equity.                          | Yes                    |
| Cizí zdroje                                       | debt                  | Clearly indicates liabilities in the form of debt.        | No                     |
| Ostatní pasiva                                    | other_liabilities     | Specifies other liabilities not classified as debt.       | No                     |

### 4. Data Type Conversion and Cleaning

| **Column Name**      | **Original Type**      | **New Type**              | **Reasoning**                                                                 |
|----------------------|------------------------|---------------------------|-------------------------------------------------------------------------------|
| audit, consolidation | object                 | Categorical               | Optimizes memory and performance for binary flags.                            |
| currency, region, etc.| object                 | Categorical               | Using categorical types for low-cardinality strings is highly memory-efficient. |
| date_founded         | object (string)        | Date                      | Converts to a proper date type for time-based analysis.                       |
| ico                  | int64                  | String                    | Treats firm identifier as a string to avoid numeric misinterpretation.         |
| num_employees        | float64                | Int32                     | Converts to integer since employee counts are whole numbers.                  |
| year                 | int32                  | Int16                     | Reduces memory footprint for the year column.                                 |
| All metric columns   | object/float           | Float64                   | Ensures all financial metrics are stored as floating-point numbers for calculations. |

### 5. Saving the Final Data

- The final wide-panel DataFrame is saved as a Parquet file using Snappy compression.  
- **Reasoning:**  
  - Parquet is a columnar storage format that offers significantly faster read/write performance and smaller file sizes compared to CSV.
  - It is the standard for storing large datasets for analytics and is ideal for the firm-year panel structure.

---

## Conclusion

This script efficiently transforms raw, multi-file MagnusWeb data into a clean, analysis-ready **firm-year wide panel**. The key steps include:

- Using **Polars' lazy engine** for memory-efficient data ingestion.
- A **melt-pivot** strategy to robustly parse time-coded columns and reshape the data.
- Standardizing column names, metrics, and data types for consistency.
- Saving the final dataset in the high-performance **Parquet** format.

This standardized structure is ideal for direct use in econometric models and facilitates easy integration with other datasets (e.g., inflation, macroeconomic data) for robust panel analysis.