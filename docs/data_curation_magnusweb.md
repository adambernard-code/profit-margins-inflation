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
| Obrat, Výnosy / Obrat Výnosy                      | turnover              | Consolidates similar revenue measures under one term.     | Yes                    |
| Tržby, Výkony / Tržby Výkony                      | sales_revenue         | Unifies turnover measures for consistency.                | Yes                    |
| Aktiva celkem                                     | total_assets          | Clearly indicates the total assets of the firm.           | Yes                    |
| Stálá aktiva                                      | fixed_assets          | Standard term for fixed assets.                           | No                     |
| Oběžná aktiva                                     | current_assets        | Indicates current assets.                                 | No                     |
| Ostatní aktiva                                    | other_assets          | Groups other asset categories under a unified term.       | No                     |
| Pasiva celkem                                     | total_liabilities_and_equity     | Standardizes liabilities reporting.                       | Yes                    |
| Vlastní kapitál                                   | equity                | Short, standard term for equity.                          | Yes                    |
| Cizí zdroje                                       | total_liabilities     | Clearly indicates liabilities in the form of debt.        | No                     |
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


## Data Dictionary

Below is a structured overview of every column in the panel dataset, grouped by category. Each entry shows the **column name**, the **original Czech term** (where applicable), and a brief **description**.

---

### 1. Static Entity Attributes

| Column              | Czech term                         | Description                                             |
| ------------------- | ---------------------------------- | ------------------------------------------------------- |
| `ico`               | IČO                                | Company Identification Number                           |
| `name`              | Název subjektu                     | Legal name of the entity                                |
| `main_nace`         | Hlavní NACE                        | Main NACE classification (text label)                   |
| `main_nace_code`    | Hlavní NACE – kód                  | Main NACE code (numeric/alphanumeric)                   |
| `sub_nace_cz`       | Vedlejší NACE CZ                   | Secondary NACE CZ classification (text label)           |
| `sub_nace_cz_code`  | Vedlejší NACE CZ – kód             | Secondary NACE CZ code                                  |
| `main_okec`         | Hlavní OKEČ                        | Main OKEČ classification (text label)                   |
| `main_okec_code`    | Hlavní OKEČ – kód                  | Main OKEČ code                                          |
| `sub_okec`          | Vedlejší OKEČ                      | Secondary OKEČ classification (text label)              |
| `sub_okec_code`     | Vedlejší OKEČ – kód                | Secondary OKEČ code                                     |
| `esa2010`           | Institucionální sektory (ESA 2010) | Institutional sector classification (ESA 2010)          |
| `esa95`             | Institucionální sektory (ESA 95)   | Institutional sector classification (ESA 95)            |
| `locality`          | Lokalita                           | Municipality or locality                                |
| `region`            | Kraj                               | Region                                                  |
| `num_employees`     | Počet zaměstnanců                  | Number of employees                                     |
| `num_employees_cat` | Kategorie počtu zaměstnanců CZ     | Employee count category (Czech classification)          |
| `turnover_cat`      | Kategorie obratu                   | Turnover category                                       |
| `audit`             | Audit                              | Audit indicator (yes/no)                                |
| `consolidation`     | Konsolidace                        | Consolidation status                                    |
| `currency`          | Měna                               | Reporting currency                                      |
| `date_founded`      | Datum vzniku                       | Date of incorporation                                   |
| `date_dissolved`    | Datum zrušení                      | Date of dissolution                                     |
| `status`            | Stav subjektu                      | Current legal status of the entity                      |
| `legal_form`        | Právní forma                       | Legal form of the entity (e.g., s.r.o., a.s.)           |
| `entity_type`       | Typ subjektu                       | Type of entity (e.g., corporation, branch, cooperative) |

---

### 2. Core Financial Statement Variables

| Column                         | Czech term                            | Description                              |
| ------------------------------ | ------------------------------------- | ---------------------------------------- |
| `profit_pre_tax`               | Hospodářský výsledek před zdaněním    | Profit before tax (EBT)                  |
| `profit_net`                   | Hospodářský výsledek za účetní období | Net profit (after tax)                   |
| `oper_profit`                  | Provozní hospodářský výsledek         | Operating profit (EBIT)                  |
| `costs`                        | Náklady                               | Total costs/expenses                     |
| `turnover`                     | Obrat, Výnosy / Obrat Výnosy          | Net turnover (total sales revenue)       |
| `sales_revenue`                | Tržby, Výkony / Tržby Výkony          | Sales revenue (production & merchandise) |
| `total_assets`                 | Aktiva celkem                         | Total assets                             |
| `fixed_assets`                 | Stálá aktiva                          | Fixed (non-current) assets               |
| `current_assets`               | Oběžná aktiva                         | Current assets                           |
| `other_assets`                 | Ostatní aktiva                        | Other assets                             |
| `total_liabilities_and_equity` | Pasiva celkem                         | Total liabilities **and** equity         |
| `equity`                       | Vlastní kapitál                       | Shareholders’ equity                     |
| `total_liabilities`            | Cizí zdroje                           | Total liabilities (external financing)   |
| `other_liabilities`            | Ostatní pasiva                        | Other liabilities                        |

---

### 3. Computed Metrics

#### 3.1 Profitability Ratios

| Column                 | Formula                                      | Description                                          |
| ---------------------- | -------------------------------------------- | ---------------------------------------------------- |
| `operating_margin_cal` | `oper_profit / sales_revenue`                | Operating margin (EBIT as a share of sales)          |
| `net_margin_cal`       | `profit_net / sales_revenue`                 | Net profit margin                                    |
| `gross_margin_cal`     | `(sales_revenue - costs) / sales_revenue`    | Approximate gross margin (1 – cost ratio)            |
| `roa_ebit_cal`         | `oper_profit / total_assets`                 | Return on assets (EBIT relative to asset base)       |
| `roe_cal`              | `profit_net / equity`                        | Return on equity (“owners’ yield”)                   |
| `roic_simple_cal`      | `oper_profit / (equity + total_liabilities)` | Return on invested capital (EBIT / capital employed) |

#### 3.2 Cost Structure Metrics

| Column           | Formula                                   | Description                                  |
| ---------------- | ----------------------------------------- | -------------------------------------------- |
| `cost_ratio_cal` | `costs / sales_revenue`                   | Cost ratio (expenses as a share of sales)    |
| `pcm_proxy_cal`  | `(sales_revenue - costs) / sales_revenue` | Price–cost margin proxy (identical to gross) |

#### 3.3 Interest & Tax Diagnostics

| Column                     | Formula                                          | Description                              |
| -------------------------- | ------------------------------------------------ | ---------------------------------------- |
| `net_interest_expense_cal` | `oper_profit - profit_pre_tax`                   | Proxy for net interest/financing expense |
| `interest_coverage_cal`    | `oper_profit / net_interest_expense_cal`         | Interest coverage ratio                  |
| `effective_tax_rate_cal`   | `(profit_pre_tax - profit_net) / profit_pre_tax` | Effective tax rate                       |

#### 3.4 Growth Dynamics (YoY)

| Column                 | Formula                              | Description                          |
| ---------------------- | ------------------------------------ | ------------------------------------ |
| `rev_growth_cal`       | `pct_change(sales_revenue) over ico` | Year-on-year revenue growth          |
| `cost_growth_cal`      | `pct_change(costs) over ico`         | Year-on-year cost growth             |
| `op_profit_growth_cal` | `pct_change(oper_profit) over ico`   | Year-on-year operating profit growth |

#### 3.5 Efficiency & Scale Metrics

| Column                   | Formula                         | Description                                       |
| ------------------------ | ------------------------------- | ------------------------------------------------- |
| `asset_turnover_cal`     | `sales_revenue / total_assets`  | Asset turnover (revenue generated per unit asset) |
| `labor_productivity_cal` | `sales_revenue / num_employees` | Labor productivity (sales per employee)           |

---
