# Data Curation Script Documentation - MagnusWeb data 

This script transforms the raw MagnusWeb data (in CSV format) into a tidy dataset that is optimized for time-series and panel analysis. The final output is saved in an efficient Parquet format. This document outlines the main actions performed by the script, along with the rationale behind key data manipulations.

---

## Overview

The script performs the following major steps:

1. **Data Loading:**  
   - Reads the raw CSV file from the specified source directory using a semicolon as a delimiter.

2. **Wide-to-Long Transformation:**  
   - Separates static (firm-level metadata) columns from time-coded columns.
   - Melts the wide-format DataFrame into a long (tidy) format, where each row represents a single observation for a given firm at a particular time period and metric.

3. **Column Parsing and Extraction:**  
   - Parses raw column names to extract time-series information such as **year**, **quarter**, and the **metric** name.
   - Handles different naming conventions (e.g., `2023/4Q Aktiva celkem`, `4Q/2001 Tržby Výkony`, and `2023 Kategorie obratu`).

4. **Column Renaming and Measure Mapping:**  
   - Renames columns to shorter, standardized English names.
   - Maps verbose measure names (e.g., `"Hospodářský výsledek před zdaněním"`) to concise names (e.g., `"profit_pre_tax"`).

5. **Data Type Conversion and Cleaning:**  
   - Converts categorical, numeric, and date columns to appropriate data types.
   - Maps binary values in `audit` and `consolidation` from Czech ("Ano"/"Ne") to English ("Yes"/"No").
   - Converts date columns to store only the date portion (without time).

6. **Saving the Final Dataset:**  
   - Saves the cleaned and transformed data as a Parquet file with Snappy compression, enhancing I/O performance and reducing file size.

---

## Detailed Actions and Rationale

### 1. Wide-to-Long Transformation

| **Action**             | **Description**                                                                                        | **Reasoning**                                                                                          |
|------------------------|--------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Identify `id_cols`     | Select static (firm-level) columns such as "IČO", "Název subjektu", "Hlavní NACE", etc.                  | These columns do not change over time and serve as firm identifiers for merging and grouping.          |
| Identify `time_cols`   | All columns not in `id_cols` are considered time-coded and will be melted into a long format.            | Time-coded columns encode both the period and the metric value, which need to be separated for analysis. |
| Melt DataFrame         | Use `pd.melt()` to convert wide-format data into a long format with columns for firm metadata, period, and value. | A tidy (long) format is more suitable for time-series and panel regression analysis.                  |

### 2. Column Parsing and Extraction

| **Example Raw Column**         | **Parsed Components**                                  | **Reasoning**                                                            |
|--------------------------------|--------------------------------------------------------|--------------------------------------------------------------------------|
| `2023/4Q Aktiva celkem`        | Year: 2023, Quarter: 4, Metric: "Aktiva celkem"         | Extracts the time and metric for longitudinal tracking.                |
| `4Q/2001 Tržby Výkony`         | Year: 2001, Quarter: 4, Metric: "Tržby Výkony"          | Handles alternative naming conventions consistently.                   |
| `2023 Kategorie obratu`        | Year: 2023, Quarter: None, Metric: "Kategorie obratu"   | Accommodates columns with only a year component.                       |

### 3. Column Renaming and Measure Mapping

#### Column Renaming

| **Original Column Name**                       | **New Column Name**  | **Reasoning**                                              |
|------------------------------------------------|----------------------|------------------------------------------------------------|
| IČO, Název subjektu, Hlavní NACE, etc.           | ico, name, main_nace, etc. | Short, standardized names facilitate coding and merging.  |

#### Measure Mapping

| **Original Measure Name**                          | **Mapped Name**       | **Reasoning**                                             |
|---------------------------------------------------|-----------------------|-----------------------------------------------------------|
| Hospodářský výsledek před zdaněním                | profit_pre_tax        | Provides a concise, standard English name.              |
| Hospodářský výsledek za účetní období             | profit_net            | Clarifies that this is the net profit measure.          |
| Provozní hospodářský výsledek                     | oper_profit           | Shortens the metric name for operating profit.          |
| Náklady                                           | costs                 | Standard term used in English.                          |
| Obrat, Výnosy / Obrat Výnosy                        | sales_revenue         | Consolidates similar revenue measures under one term.   |
| Tržby, Výkony / Tržby Výkony                       | turnover              | Unifies turnover measures for consistency.              |
| Aktiva celkem                                     | total_assets          | Clearly indicates the total assets of the firm.         |
| Stálá aktiva                                     | fixed_assets          | Standard term for fixed assets.                         |
| Oběžná aktiva                                     | current_assets        | Indicates current assets.                               |
| Ostatní aktiva                                    | other_assets          | Groups other asset categories under a unified term.     |
| Pasiva celkem                                     | total_liabilities     | Standardizes liabilities reporting.                     |
| Vlastní kapitál                                   | equity                | Short, standard term for equity.                        |
| Cizí zdroje                                       | debt                  | Clearly indicates liabilities in the form of debt.      |
| Ostatní pasiva                                    | other_liabilities     | Specifies other liabilities not classified as debt.     |

### 4. Data Type Conversion and Cleaning

| **Column Name**      | **Original Type**      | **New Type**              | **Reasoning**                                                                 |
|----------------------|------------------------|---------------------------|-------------------------------------------------------------------------------|
| audit, consolidation | object                 | category                  | Facilitates grouping and filtering; mapping to "Yes"/"No for clarity.          |
| currency             | object                 | category                  | Standardizes currency values to "CZK" and "EUR"; reduces memory usage.         |
| date_founded         | object                 | datetime.date             | Converts to date for easier date comparisons (time portion is not needed).     |
| date_dissolved       | float64                | datetime.date             | Maintained for potential future use; converted to date.                      |
| ico                  | int64                  | string                    | Treats firm identifier as a string to avoid numeric misinterpretation.         |
| num_employees        | float64                | Int64                     | Converts to integer since employee counts should be whole numbers.           |
| quarter, year        | float64                | Int64                     | Stores time-series values as integers for consistency in analysis.           |
| Various classification columns (e.g., main_nace, sub_okec_code) | object/float64 | category | Using categorical types optimizes memory and improves grouping performance. |

### 5. Value Mapping for Binary Columns

| **Column**      | **Mapping**                | **Reasoning**                                               |
|-----------------|----------------------------|-------------------------------------------------------------|
| audit           | "Ano" → "Yes", "Ne" → "No" | Converts Czech binary responses to English for consistency.  |
| consolidation   | "Ano" → "Yes", "Ne" → "No" | Same reasoning as above.                                     |

### 6. Saving the Final Data

- The final cleaned DataFrame is saved as a Parquet file using Snappy compression.  
- **Reasoning:**  
  - Parquet offers faster read/write performance and smaller file sizes compared to CSV.
  - It is especially beneficial for large datasets and subsequent analyses.

---

## Conclusion

This script converts the raw MagnusWeb data into a tidy, efficient, and analysis-ready format. The transformation includes:

- Converting wide data into long format with explicit time information.
- Renaming columns and mapping verbose measure names to concise English equivalents.
- Converting data types for improved performance and consistency.
- Mapping binary values to English.
- Saving the final dataset in Parquet format for efficient storage and fast I/O.

This standardized structure will facilitate easier integration with other datasets (e.g., inflation, macroeconomic data, and additional NACE references) and support robust time-series and panel analysis.

## Newly added Measures: 

- datum vzniku (date founded)
- datum zrusení (date dissolved)