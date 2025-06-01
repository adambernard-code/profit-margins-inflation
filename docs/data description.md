# Data Documentation

This document provides a detailed description of the Parquet files used in this thesis. Each section outlines the purpose, variables, and data sources for a specific file.

---

## 1. `economy_annual_tidy.parquet`

### 1.1. Purpose

This file consolidates several key macroeconomic indicators for the Czech Republic on an annual basis. It merges the following data:

* CNB Repo Rates (time-weighted annual average)
* HICP (December value)
* Average Wages (CZSO)
* GDP (nominal and constant 2020 prices)
* Unemployment Rate (CZSO)
* CZK/EUR Exchange Rate (CNB)

After merging by year, all indicators are pivoted into a tidy (long) format, with one observation per row, identified by a `year`–`metric` combination.

### 1.2. Variables and Definitions

| Variable | Type            | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `year`   | Integer         | Calendar year of the observation. (Range: \~2000–2024)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `metric` | String/Category | Identifier for the economic indicator represented in the `value` column. Possible values include:<br> - `cnb_repo_rate_annual`: Time-weighted annual average CNB 2W Repo Rate (percent).<br> - `hicp_dec`: HICP Overall Index for December (index base can vary by ECB standards; represents end-of-year price level, base = previous year - December).<br> - `nom_gr_avg_wage_czk`: Average nominal gross monthly wage in CZK (per full-time equivalent).<br> - `no_of_employees_ths`: Number of employees (in thousands).<br> - `gdp_nominal_prices`: Nominal GDP (CZK millions).<br> - `gdp_2020_base_prices`: Real GDP in constant 2020 prices (CZK millions).<br> - `gdp_2020_base_prices_sopr`: Year-over-year index/volume change (SOPR ratio = stejně období předchozího roku) in 2020 prices.<br> - `deflator_nominal`: GDP deflator (SOPR ratio).<br> - `deflator_base_2020`: An additional GDP deflator variant with 2020 as the base year.<br> - `unemp_rate`: Unemployment rate (percent).<br> - `fx_czk_eur_annual_avg`: Average annual exchange rate (CZK per EUR). |
| `value`  | Float           | The numeric value of the `metric` for the given `year`. Units and interpretation depend on the specific `metric`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

### 1.3. Notes

* All data is annual, generally covering the period from 2000 to 2024, contingent on availability for each specific metric.
* The dataset is structured in a **long/tidy format**, meaning each row represents a single time-series observation for a specific metric and year.

### 1.4. Data Sources

| Metric Name                      | Source File / Origin                                                   |
| -------------------------------- | ---------------------------------------------------------------------- |
| CNB Repo Rate (Annual)           | CNB: `CNB_repo_sazby.txt` (repo rate decisions text file)              |
| HICP (December values)           | ECB Data Portal: `ECB Data Portal_20250402011223_HICP_from1996_CZ.csv` |
| Nominal Gross Average Wage (CZK) | CZSO: `pmzcr030625_1_wages_avg.xlsx`                                   |
| Number of Employees (Thousands)  | CZSO: `pmzcr030625_1_wages_avg.xlsx`                                   |
| GDP (Nominal Prices)             | CZSO: `NUCDUSHV01-R_CZSO_GDP.xlsx`                                     |
| GDP (2020 Base Prices)           | CZSO: `NUCDUSHV01-R_CZSO_GDP.xlsx`                                     |
| GDP (2020 Base Prices SOPR)      | CZSO: `NUCDUSHV01-R_CZSO_GDP.xlsx`                                     |
| Deflator (Nominal)               | CZSO: `NUCDUSHV01-R_CZSO_GDP.xlsx`                                     |
| Deflator (Base 2020)             | CZSO: `NUCDUSHV01-R_CZSO_GDP.xlsx`                                     |
| Unemployment Rate                | CZSO: `ZAMDPORK02_unemployment.xlsx`                                   |
| FX CZK/EUR (Annual Average)      | CNB: `CNB FX rates from 1999.txt`                                      |

---

## 2. `data_by_nace_annual_tidy.parquet`

### 2.1. Purpose

This file provides a long-format dataset of annual CZSO indicators categorized by NACE (Statistical Classification of Economic Activities in the European Community) codes, covering the years 2000–2024. It includes:

* Industrial PPI (Producer Price Index for NACE divisions B–E; base 2015 = 100)
* Aggregated SPPI (Service Producer Price Index for sections outside industry, re-based to 2015 = 100)
* Unified PPI (a concatenation of the industrial PPI and aggregated SPPI)
* Average Wages (gross monthly CZK per full-time equivalent)
* Number of Employees (in thousands)

Each row in this dataset represents a single observation for a specific (`czso_code`, `year`, `metric`) combination.

### 2.2. Variables and Definitions

| Variable    | Type    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `czso_code` | String  | NACE code or an aggregated code (e.g., `"A"`, `"011+012+013"`, `"B+C+D+E"`, `"G+H+I+J+K+L+M+N"`).                                                                                                                                                                                                                                                                                                                                                                              |
| `level`     | Integer | Classification depth of the NACE code:<br> - `0` = Top-level aggregate (e.g., `"B+C+D+E"`)<br> - `1` = One-letter division (e.g., `"A"`, `"B"`)<br> - `2` = Two-digit subdivision (e.g., `"49"`, `"58"`)                                                                                                                                                                                                                                                                       |
| `name_cs`   | String  | Czech label for the NACE code (e.g., “Průmysl” for `"B+C+D+E"`).                                                                                                                                                                                                                                                                                                                                                                                                               |
| `name_en`   | String  | English label for the NACE code (fallback to Czech source text if no translation is available).                                                                                                                                                                                                                                                                                                                                                                                |
| `year`      | Integer | Calendar year of the observation (2000 – 2024).                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `metric`    | String  | Identifier for the indicator. Possible values:<br> - `ppi_by_nace_industry`: Industrial PPI (NACE divisions B–E; from CZSO “industry” sheet).<br> - `ppi_by_nace_aggregated`: SPPI for non‐industry sections (rebased to 2015 = 100).<br> - `ppi_by_nace`: Combined PPI series (concatenation of the two above).<br> - `avg_wages_by_nace`: Average gross monthly wage in CZK (per full‐time equivalent).<br> - `no_of_employees_by_nace`: Number of employees (in thousands). |
| `value`     | Float   | Numeric value of the `metric`. Missing values are represented as `NaN`.                                                                                                                                                                                                                                                                                                                                                                                                        |
| `unit`      | String  | Unit of measure for the `value`. Possible values:<br> - `"2015=100"` (for all PPI metrics)<br> - `"CZK_avg_gross_monthly_per_fulltime"` (for wages)<br> - `"ths"` (for number of employees)                                                                                                                                                                                                                                                                                    |
| `source`    | String  | Indicates the CZSO subset from which the data row originated. Possible values:<br> - `"CZSO – industry"` (for industrial PPI)<br> - `"CZSO – without industry"` (for aggregated SPPI)<br> - `"CZSO"` (for wages and employees)                                                                                                                                                                                                                                                 |

### 2.3. Key Transformations

1. **Industrial PPI**

   * Data read from CZSO’s IR15 yearly sheet.
   * Filtered for NACE divisions B–E; rows before the year 2000 were dropped.
   * Values like `":"` or `"i.d."` were converted to `NaN`.

2. **SPPI (Aggregated)**

   * Data read from CZSO SPPI Table 1.1.
   * Rows for NACE division B+C+D+E and the `"G+H+I+J+K+L+M+N-731"` series were dropped.
   * Agriculture codes (originally base 2020) were re-based to 2015=100.
   * Only years ≥ 2000 were retained.

3. **Unified PPI**

   * Created by concatenating the industrial and aggregated SPPI dataframes.
   * Overlap was avoided by excluding industrial codes from the aggregated SPPI subset before concatenation.

4. **Wages / Employees**

   * Data read from CZSO Q1–Q4 sheets; these four quarters were combined to calculate an annual average.
   * Codes like `"B+C+D+E"` were normalized to `"Průmysl / Industry"`.
   * Only years 2000–2024 were retained.

5. **Final Merge**

   * Each source dataset was melted (pivoted longer) so that `year` became a row attribute.
   * All five resulting dataframes (industrial PPI, aggregated SPPI, unified PPI, wages, employees) were concatenated into a single dataframe.
   * The final consolidated dataset was saved as `data_by_nace_annual_tidy.parquet`.

### 2.4. Data Sources

| Metric / Data Element            | Source File / Origin                                           |
| -------------------------------- | -------------------------------------------------------------- |
| PPI by NACE (industrial)         | CZSO: `ipccr031725_21_CSU_PPI_by_NACE_industry.xlsx`           |
| SPPI by NACE (aggregated)        | CZSO: `ipccr052025_11_CSU_PPI_an_SPPI_by_NACE_aggregated.xlsx` |
| Avg. Gross Monthly Wage by NACE  | CZSO: `pmzcr030625_2_wages by NACE.xlsx`                       |
| Avg. Number of Employees by NACE | CZSO: `pmzcr030625_3_csu avg number of employees by nace.xlsx` |

---

## 3. `data_by_nace_annual_tidy_propagated.parquet`

### 3.1. Purpose

This file consolidates the original NACE-level time series data (for wages, number of employees, and PPI from `data_by_nace_annual_tidy.parquet`) and fills in missing values at lower NACE levels. Missing values are imputed by "propagating" them from higher-level (parent) or umbrella NACE codes. Each row represents one (`czso_code`, `year`, `metric`) observation, including both original and newly imputed values.

### 3.2. Variables and Definitions

| Variable      | Type            | Description                                                                                                                                                                                                                                                                                                                             |
| ------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `czso_code`   | String          | NACE code (e.g., `"A"`, `"011+012+013"`, `"B+C+D+E"`) for which a value exists or has been propagated.                                                                                                                                                                                                                                  |
| `magnus_nace` | String          | Corresponding “Magnus” NACE code, derived from the `t_nace_matching.parquet` table. Useful for joining to firm‐level records.                                                                                                                                                                                                           |
| `level`       | Integer         | NACE hierarchy depth: `0` (umbrella/aggregate), `1` (division), `2` (subdivision), etc.                                                                                                                                                                                                                                                 |
| `name_cs`     | String          | Czech label for the NACE code.                                                                                                                                                                                                                                                                                                          |
| `name_en`     | String          | English label for the NACE code (or fallback to Czech label).                                                                                                                                                                                                                                                                           |
| `year`        | Integer         | Calendar year of the observation (2000 – 2024).                                                                                                                                                                                                                                                                                         |
| `metric`      | String/Category | Type of indicator. Possible values:<br> - `avg_wages_by_nace`: Average gross monthly wage (CZK) per full-time equivalent.<br> - `no_of_employees_by_nace`: Number of employees (in thousands).<br> - `ppi_by_nace`: Combined Producer Price Index (2015 = 100) for industrial and service aggregates.                                   |
| `value`       | Float           | Measured or imputed numeric value for the (`czso_code`, `year`, `metric`) combination.                                                                                                                                                                                                                                                  |
| `unit`        | String/Category | Unit of measure, corresponding to the `metric`:<br> - `"CZK_avg_gross_monthly_per_fulltime"` (for wages)<br> - `"ths"` (for number of employees)<br> - `"2015=100"` (for PPI)                                                                                                                                                           |
| `source`      | String          | Indicates how the row's value was obtained:<br> - Original source (e.g., `"CZSO"`, `"CZSO – industry"`, `"CZSO – without industry"`) if the value was present in the raw data.<br> - `"PROPAGATED from level X (CODE)"` if the value was imputed by ascending the NACE hierarchy from a parent code (specified by `CODE`) at level `X`. |

### 3.3. Notes on Data Sources and Transformations

1. **Underlying Inputs**

   * The primary data input is the `data_by_nace_annual_tidy.parquet` file, which contains observed values for three metrics: `avg_wages_by_nace`, `no_of_employees_by_nace`, and `ppi_by_nace` at various NACE levels.
   * The NACE hierarchy and parent-child relationships are derived from the `t_nace_matching.parquet` table.

2. **Propagation Logic**

   * **Full Grid Creation**: A complete set of rows is constructed for every combination of NACE code (from the hierarchy table), year (2000–2024), and metric.
   * **Identify Missing Values**: Any (`czso_code`, `year`, `metric`) combination not present in the original `data_by_nace_annual_tidy.parquet` dataset is flagged as missing.
   * **Recursive Search for Imputation**:

     * For each missing data point, the algorithm checks its immediate parent code (level – 1) in the NACE hierarchy.
     * If the parent code has a non-missing value for the same year and metric, that value is copied down to the missing entry.
     * If the immediate parent's value is also missing, the search continues upwards to the next hierarchical level (grandparent), and so on, until a non-missing value is found or the top of the NACE hierarchy is reached.
   * **Umbrella Code Fallback**: If no direct ancestor in the hierarchy has a value, the algorithm can propagate a value from a higher-level aggregate code (e.g., from `"B+C+D+E"` for any industrial division B, C, D, or E). In practice, level-0 codes (aggregates) typically have their values "expanded" to individual divisions before propagation, so most missing entries at levels 1 or 2 are filled from their closest ancestor or the relevant umbrella code if available.
   * **Source Tagging**: Each row imputed through this process has its `source` column updated to `"PROPAGATED from level X (PARENT_CODE)"`, recording the NACE code and level from which the value was derived.

3. **Final Cleanup**

   * Any rows whose `czso_code` does not appear in the NACE hierarchy table (`t_nace_matching.parquet`) are dropped.
   * The final table is merged (left-join) with `t_nace_matching.parquet` to add the `magnus_nace` column, mapping CZSO NACE codes to Magnus NACE codes.
   * The resulting dataset, including both observed and imputed values, is saved to `data_by_nace_annual_tidy_propagated.parquet`.

4. **Usage**

   * This dataset allows downstream analyses to distinguish between "true" observations (where the `source` column does not contain `"PROPAGATED"`) and imputed values.
   * Because all NACE codes present in the hierarchy now have a data row for every year and metric (either observed or imputed), it facilitates the computation of complete bottom-up indicators (e.g., aggregating subdivision data into divisions) without gaps due to missing data.

By incorporating both observed and hierarchically imputed values, this propagated dataset ensures that every NACE code has a definitive value for each year and metric, promoting consistent time-series analyses across all levels of the NACE classification.

---

## 4. `magnusweb_tidy.parquet`

### 4.1. Purpose

This file contains **firm-level** accounting and descriptive data exported from the MagnusWeb database (original file: `export-7.csv`). The script processes this data by reshaping it from a wide format to a long (tidy) format. Time-coded columns (e.g., “2023/4Q Hospodářský výsledek před zdaněním”) are parsed into distinct `year`, `quarter`, and `metric` columns.

### 4.2. Variables and Definitions

#### Firm Identification and Descriptive Fields

| Variable           | Type               | Description                                                                                                       | Original Name                      |
| ------------------ | ------------------ | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `ico`              | String             | The firm’s unique identification number (IČO).                                                                    | IČO                                |
| `name`             | String             | The firm’s name (Název subjektu).                                                                                 | Název subjektu                     |
| `main_nace`        | Category           | Textual description of the firm's main NACE activity.                                                             | Hlavní NACE                        |
| `main_nace_code`   | String             | Code for the firm's main NACE activity.                                                                           | Hlavní NACE - kód                  |
| `sub_nace_cz`      | Category           | Textual description of an additional (secondary) NACE activity. May be missing.                                   | Vedlejší NACE CZ                   |
| `sub_nace_cz_code` | String             | Code for an additional (secondary) NACE activity. May be missing.                                                 | Vedlejší NACE CZ - kód             |
| `main_okec`        | Category           | Textual description of the OKEČ classification (predecessor to NACE in CZ). May be missing.                       | Hlavní OKEČ                        |
| `main_okec_code`   | String             | Code for the OKEČ classification. May be missing.                                                                 | Hlavní OKEČ - kód                  |
| `sub_okec`         | Category           | Textual description of an additional OKEČ classification, if available.                                           | Vedlejší OKEČ                      |
| `sub_okec_code`    | String             | Code for an additional OKEČ classification, if available.                                                         | Vedlejší OKEČ - kód                |
| `esa2010`          | Category           | Firm’s institutional sector classification under ESA 2010, if provided.                                           | Institucionální sektory (ESA 2010) |
| `esa95`            | Category           | Firm’s institutional sector classification under ESA 95, if provided.                                             | Institucionální sektory (ESA 95)   |
| `locality`         | Category           | Geographical location of the firm (e.g., city/district).                                                          | Lokalita                           |
| `region`           | Category           | Higher-level geographical region of the firm.                                                                     | Kraj                               |
| `num_employees`    | Integer (nullable) | Stated number of employees.                                                                                       | Počet zaměstnanců                  |
| `turnover_cat`     | Category           | Category of turnover (e.g., "500 000 000 - 999 999 999 Kč").                                                      | Kategorie obratu                   |
| `audit`            | Category           | Indicates whether the firm undergoes statutory audit. Possible values: `"Yes"`, `"No"`, or missing.               | Audit                              |
| `consolidation`    | Category           | Indicates whether the firm’s financial statements are consolidated. Possible values: `"Yes"`, `"No"`, or missing. | Konsolidace                        |
| `currency`         | Category           | Currency used for the firm’s financial statements in the source. Possible values: `"CZK"`, `"EUR"`, or missing.   | Měna                               |
| `date_founded`     | Date (YYYY-MM-DD)  | Firm's registration date. May be missing.                                                                         | Datum vzniku                       |
| `date_dissolved`   | Date (YYYY-MM-DD)  | Firm's dissolution date (if dissolved). May be missing.                                                           | Datum zrušení                      |

---

#### Time and Accounting/Financial Data Fields

| Variable  | Type               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Original Name |
| --------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| `year`    | Integer (nullable) | Reporting year for the melted accounting/financial data.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | year          |
| `quarter` | Integer (nullable) | Reporting quarter (1–4). If data is annual-only, this may be `NaN`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | quarter       |
| `metric`  | Category/String    | Type of financial statement item or indicator. Key mappings include:<br>- `profit_pre_tax` (Hospodářský výsledek před zdaněním)<br>- `profit_net` (Hospodářský výsledek za účetní období)<br>- `oper_profit` (Provozní hospodářský výsledek)<br>- `costs` (Náklady)<br>- `sales_revenue` (Obrat / Výnosy / Tržby)<br>- `turnover` (Tržby, Výkony)<br>- `total_assets` (Aktiva celkem)<br>- `fixed_assets` (Stálá aktiva)<br>- `current_assets` (Oběžná aktiva)<br>- `other_assets` (Ostatní aktiva)<br>- `total_liabilities` (Pasiva celkem)<br>- `equity` (Vlastní kapitál)<br>- `debt` (Cizí zdroje)<br>- `other_liabilities` (Ostatní pasiva) | metric        |
| `value`   | Float              | The numeric figure for the chosen `metric`. Units (e.g., thousands or full currency units) depend on the original source data. The `currency` column indicates if values are in CZK or EUR.                                                                                                                                                                                                                                                                                                                                                                                                                                                      | value         |

---

### 4.3. Notes

* Each row represents a single financial metric for a specific firm in a given year and quarter.
* If the original data column did not contain quarterly information (i.e., it was annual data), the `quarter` field is `NaN`.
* Some firms or rows may have missing data (NaN) in the `value` column for certain periods or metrics.

### 4.4. Data Sources

| Data Element                              | Source File / Origin      |
| ----------------------------------------- | ------------------------- |
| Firm-level financial and descriptive data | MagnusWeb: `export-7.csv` |

---

## 5. `t_nace_matching.parquet`

### 5.1. Purpose

This file provides a cleaned, hierarchical mapping of NACE Rev. 2 codes, based on CZSO classifications. It includes Czech and English short labels, incremental codes for each NACE level, a Eurostat-style “full\_nace” path string, a padded Magnus format NACE code, and an industry-sector indicator. This table is fundamental for all NACE-based joins and data propagation logic in other datasets.

### 5.2. Variables and Definitions

| Variable        | Type    | Description                                                                                                                                                                                                                                                       |
| --------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name_czso_cs`  | String  | Czech short description (abbreviated text) of the NACE item (e.g., “Zemědělství” for code “A”). From CZSO.                                                                                                                                                        |
| `name_czso_en`  | String  | English short description of the NACE item. Imported from the CZSO English NACE classification CSV.                                                                                                                                                               |
| `level`         | Integer | Hierarchy depth in the NACE structure:<br> - `1` = Top NACE section (letter)<br> - `2`–`5` = Successive numeric subdivisions (e.g., division, group, class, sub-class)                                                                                            |
| `czso_code`     | String  | Raw NACE code string as provided by CZSO (`chodnota`). Examples:<br> - Level 1: Single letter (e.g., “A”, “B”)<br> - Level 2+: Full numeric strings (e.g., “011”, “0111”)                                                                                         |
| `level1_code`   | String  | Top-level NACE letter (e.g., "A", "B"). This code is the same for all NACE items that are descendants under this branch.                                                                                                                                          |
| `level2_code`   | String  | Incremental code at NACE Level 2: the full numeric code (e.g., “01”, “011”). Empty if the record is at Level 1.                                                                                                                                                   |
| `level3_code`   | String  | Incremental code at NACE Level 3: the suffix that distinguishes this item from its parent’s Level 2 code. Empty for NACE levels < 3.                                                                                                                              |
| `level4_code`   | String  | Incremental code at NACE Level 4: the suffix that distinguishes this item from its parent’s Level 3 code. Empty for NACE levels < 4.                                                                                                                              |
| `level5_code`   | String  | Incremental code at NACE Level 5: the suffix that distinguishes this item from its parent’s Level 4 code. Empty for NACE levels < 5.                                                                                                                              |
| `full_nace`     | String  | Compact hierarchical NACE string in Eurostat style, constructed as `<letter>.<inc2>.<inc3>.<inc4>.<inc5>`.                                                                                                                                                        |
| `magnus_nace`   | String  | A standardized NACE code format:<br> - If `level` is 1: Equals `level1_code` (letter).<br> - If `level` is 2–4: `czso_code` padded with trailing zeros to a length of six digits (e.g., “105” → “105000”).<br> - If `level` is 5: Left as an empty string (`""`). |
| `industry_flag` | Boolean | `True` if the `level1_code` (NACE section letter) is B, C, D, or E (indicating an industrial sector). Otherwise `False`.                                                                                                                                          |

### 5.3. Notes on Data Sources and Transformations

1. **Original Input**

   * The primary data sources are CZSO’s NACE Rev. 2 classification CSV files:

     * `KLAS80004_CS_NACE_classification.csv` (for Czech labels)
     * `KLAS80004_EN_NACE_classification.csv` (for English labels)
   * Each row in these source files typically contained columns such as `uroven` (level), `chodnota` (code), `zkrtext` (short name), and `nadvaz` (parent pointer), along with other metadata.

2. **Ancestry Extraction**

   * For every NACE item (row) in the source data, its ancestry was traced by iteratively following the `nadvaz` (parent pointer) up to Level 1. This built a reversed list of `(uroven, chodnota)` pairs, representing the path from Level 1 down to the current NACE item.

3. **Incremental Codes**

   * The top-level letter (`level1_code`) was identified from the first ancestor in the traced path.
   * Numeric codes at levels 2 and above were collected. For the first numeric level (typically NACE Level 2), the entire code was stored. For subsequent numeric levels (3, 4, 5), the parent’s full code prefix was removed to derive the “incremental” portion specific to that level.

4. **`full_nace` Construction**

   * The `full_nace` string was constructed by joining the `level1_code` with all applicable incremental codes, separated by dots (`.`). This construction ensures that the string accurately reflects the actual hierarchical path, even if some intermediate numeric levels are missing in the specific code.

5. **`magnus_nace` Computation**

   * If `level` is 1, `magnus_nace` is set to the `level1_code` (the letter).
   * If `level` is between 2 and 4 (inclusive), `magnus_nace` is created by right-padding the `czso_code` with zeros to a total length of 6 characters.
   * If `level` is 5, `magnus_nace` is left as an empty string, as this NACE depth is not typically used in the Magnus format.

6. **`industry_flag`**

   * This boolean flag is set to `True` if the `level1_code` is one of “B”, “C”, “D”, or “E” (standard industrial sections). Otherwise, it is set to `False`.

7. **English Label Enrichment**

   * The English NACE classification CSV was loaded, and English labels (`name_czso_en`) were matched to their Czech counterparts based on the `chodnota` (CZSO code). If no matching English label was found for a code, the `name_czso_en` field was left as an empty string.

8. **Final Cleanup & Output**

   * Columns were reordered to ensure `name_czso_en` immediately follows `name_czso_cs` for better readability.
   * The resulting DataFrame, containing the complete NACE hierarchy and associated codes/labels, was saved as `t_nace_matching.parquet`.

9. **Usage**

   * This table is a crucial reference for understanding NACE code structures. It provides each code’s lineage (via `levelX_code` fields and `full_nace`), a `magnus_nace` code for matching with MagnusWeb firm data, and a simple `industry_flag`. All NACE-based data propagation or roll-up logic in other datasets relies on the parent pointers and incremental codes defined in this table.