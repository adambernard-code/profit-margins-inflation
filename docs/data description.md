
1. **Filename and Purpose**  
2. **Variables (Columns) and Data Types**  
3. **Possible Values / Definitions**  
4. **Notes on Data Sources and Transformations**

---

## 1. **`economy_annual_tidy.parquet`**

### Purpose
This file consolidates several macroeconomic indicators on an annual basis. It merges:
- **CNB Repo Rates** (time-weighted annual average)
- **HICP** (December value)
- **Average Wages** (CZSO)
- **GDP** (nominal and constant 2020 prices)
- **Unemployment Rate** (CZSO)
- **CZK/EUR Exchange Rate** (CNB)

After merging by year, all wide columns are pivoted into a tidy format with one observation per row (per `year`–`metric` combination).

### Variables and Definitions

1. **`year`**  
   - *Type*: Integer (range ~2000–2024)  
   - *Description*: Calendar year.

2. **`metric`**  
   - *Type*: String/Category  
   - *Description*: Identifies which economic indicator the `value` column represents. The main `metric` values here are:  
     - `cnb_repo_rate_annual`: Time-weighted annual average CNB 2W Repo Rate (percent).  
     - `hicp_dec`: HICP Overall Index for December (index base can vary by ECB standards; it represents the end-of-year price level, base = previous year - December).  
     - `nom_gr_avg_wage_czk`: Average nominal gross monthly wage in CZK (per full-time equivalent), from CZSO.  
     - `no_of_employees_ths`: Number of employees in thousands, from CZSO data.  
     - `gdp_nominal_prices`: Nominal GDP (CZK millions), from CZSO.  
     - `gdp_2020_base_prices`: Real GDP in constant 2020 prices (CZK millions), from CZSO.  
     - `gdp_2020_base_prices_sopr`: Year-over-year index/volume change (SOPR ratio = stejne obdobi predchoziho roku) in 2020 prices, from CZSO.  
     - `deflator_nominal`: GDP deflator (SOPR ratio), from CZSO.  
     - `deflator_base_2020`: An additional GDP deflator variant with 2020 as the base year, from CZSO.  
     - `unemp_rate`: Unemployment rate (percent), from CZSO.  
     - `fx_czk_eur_annual_avg`: Average annual exchange rate (CZK per EUR), from CNB.  

3. **`value`**  
   - *Type*: Float  
   - *Description*: The numeric value of the chosen `metric` for the given `year`. Units and meaning depend on `metric`.

### Notes
- All data is annual, covering 2000 to 2024 (depending on availability).  
- Data sources include CNB, CZSO, and ECB (for HICP).
- The dataset is **long/tidy**: each row is a single time-series observation.
- sources: 

### Sources: 


| Metric Name             | Source                                                                                                            |
|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| CNB Repo Rate (Annual)  | CNB repo rate decisions (text file `CNB_repo_sazby.txt`)                                                                     |
| HICP (December values)  | ECB Data Portal (`ECB Data Portal_20250402011223_HICP_from1996_CZ.csv`)                                                      |
| Nominal Gross Average Wage (CZK) | CZSO (Excel file: `pmzcr030625_1_wages_avg.xlsx`)                                                         |
| Number of Employees (Thousands) | CZSO (Excel file: `pmzcr030625_1_wages_avg.xlsx`)                                                         |
| GDP (Nominal Prices)    | CZSO (Excel file: `NUCDUSHV01-R_CZSO_GDP.xlsx`)                                                         |
| GDP (2020 Base Prices)  | CZSO (Excel file: `NUCDUSHV01-R_CZSO_GDP.xlsx`)                                                         |
| GDP (2020 Base Prices SOPR) | CZSO (Excel file: `NUCDUSHV01-R_CZSO_GDP.xlsx`)                                                         |
| Deflator (Nominal)      | CZSO (Excel file: `NUCDUSHV01-R_CZSO_GDP.xlsx`)                                                         |
| Deflator (Base 2020)    | CZSO (Excel file: `NUCDUSHV01-R_CZSO_GDP.xlsx`)                                                         |
| Unemployment Rate       | CZSO (Excel file: `ZAMDPORK02_unemployment.xlsx`)                                                       |
| FX CZK/EUR (Annual Average) | CNB (Text file: `CNB FX rates from 1999.txt`)                                                            |

---

## 2. **`data_by_nace_annual_tidy.parquet`**

**Purpose**
A long-format dataset of annual CZSO indicators by NACE code (2000–2024). It includes:

* **Industrial PPI** (Producer Price Index, divisions B–E; base 2015 = 100)
* **Aggregated SPPI** (Service PPI for sections outside industry, re-based to 2015 = 100)
* **Unified PPI** (concatenation of the two above)
* **Average Wages** (gross monthly CZK per full-time equivalent)
* **Number of Employees** (in thousands)

Each row is one (`czso_code`, `year`, `metric`) observation.

---

### Columns

* **`czso_code`** *(string)*
  NACE code or aggregated code (e.g., `"A"`, `"011+012+013"`, `"B+C+D+E"`, `"G+H+I+J+K+L+M+N"`).
* **`level`** *(int)*
  Classification depth:

  * `0` = Top–level (e.g., `"B+C+D+E"`)
  * `1` = One-letter division (e.g., `"A"`, `"B"`)
  * `2` = Two-digit subdivision (e.g., `"49"`, `"58"`)
* **`name_cs`** *(string)*
  Czech label for the code. (“Průmysl” for `"B+C+D+E"`, etc.)
* **`name_en`** *(string)*
  English label (or fallback to the Czech source text if no translation available).
* **`year`** *(int)*
  Calendar year (2000 – 2024).
* **`metric`** *(string)*

  * `ppi_by_nace_industry`: Industrial PPI (divisions B–E; CZSO “industry” sheet)
  * `ppi_by_nace_aggregated`: SPPI for non‐industry sections (rebased to 2015 = 100)
  * `ppi_by_nace`: Combined PPI series (concatenate the two above)
  * `avg_wages_by_nace`: average CZK gross monthly wage in (average per full‐time equivalent)
  * `no_of_employees_by_nace`: Employees (in thousands)
* **`value`** *(float)*
  Numeric value of the chosen metric. Missing values are `NaN`.
* **`unit`** *(string)*

  * `"2015=100"` for any PPI metric
  * `"CZK_avg_gross_monthly_per_fulltime"` for wages
  * `"ths"` for number of employees
* **`source`** *(string)*
  Indicates which CZSO subset provided the row:

  * `"CZSO – industry"` for industrial PPI
  * `"CZSO – without industry"` for aggregated SPPI
  * `"CZSO"` for wages and employees

---

### Key Transformations

1. **Industrial PPI**

   * Read from CZSO’s IR15 yearly sheet.
   * divisions B–E, dropped pre-2000 rows.
   * `":"` or `"i.d."` → `NaN`.

2. **SPPI (Aggregated)**

   * Read from CZSO SPPI Table 1.1.
   * Dropped division B+C+D+E rows and the `"G+H+I+J+K+L+M+N-731"` series.
   * Re-based agriculture codes (base 2020→2015).
   * Kept years ≥ 2000.

3. **Unified PPI**

   * Concatenated the industrial and aggregated PPI dataframes.
   * Overlap avoided by excluding industrial codes from the aggregated subset.

4. **Wages / Employees**

   * Read from CZSO Q1–Q4 sheets, combined those four quarters into one annual average.
   * Normalized `"B+C+D+E"` codes to `"Průmysl / Industry"`.
   * Kept years 2000–2024.

5. **Final Merge**

   * Each source was melted so that `year` is a row attribute.
   * All five dataframes (two PPI subsets, unified PPI, wages, employees) were concatenated into one.
   * Saved as `data_by_nace_annual_tidy.parquet`.

6. Data Sources Table: 

| Metric Name                  | Source                                                                       |
|------------------------------|------------------------------------------------------------------------------|
| PPI by NACE (industrial)     | CZSO (Excel file: `ipccr031725_21_CSU_PPI_by_NACE_industry.xlsx`)   |
| SPPI by NACE aggregated      | CZSO (Excel file: `ipccr052025_11_CSU_PPI_an_SPPI_by_NACE_aggregated.xlsx`) |
| Average Gross Monthly Wage by NACE | CZSO (Excel file: `pmzcr030625_2_wages by NACE.xlsx`)             |
| Average Number of Employees by NACE | CZSO (Excel file: `pmzcr030625_3_csu avg number of employees by nace.xlsx`) |


## 4. **`data_by_nace_annual_tidy_propagated.parquet`**

### Purpose

Consolidates the original NACE‐level series (wages, employees, PPI) and fills in any missing lower‐level values by “propagating” from higher‐level or umbrella codes. Each row represents one (`czso_code`, `year`, `metric`) observation, with newly imputed values where data was originally absent.

---

### Variables and Definitions

1. **`czso_code`**

   * *Type*: String
   * *Description*: NACE code (e.g., `"A"`, `"011+012+013"`, `"B+C+D+E"`, etc.) for which a value exists or has been propagated.

2. **`magnus_nace`**

   * *Type*: String
   * *Description*: Corresponding “Magnus” NACE code (from the matching table). Useful for joining to firm‐level records.

3. **`level`**

   * *Type*: Integer
   * *Description*: NACE hierarchy depth (0 = umbrella/aggregate, 1 = division, 2 = subdivision, etc.).

4. **`name_cs`**

   * *Type*: String
   * *Description*: Czech label for the NACE code.

5. **`name_en`**

   * *Type*: String
   * *Description*: English label (or fallback to Czech) for the NACE code.

6. **`year`**

   * *Type*: Integer
   * *Description*: Calendar year of the observation (2000 – 2024).

7. **`metric`**

   * *Type*: String/Category
   * *Possible values*:

     * `avg_wages_by_nace` – Average gross monthly wage (CZK) per full-time equivalent.
     * `no_of_employees_by_nace` – Number of employees (in thousands).
     * `ppi_by_nace` – Combined Producer Price Index (2015 = 100) for industrial and service aggregates.

8. **`value`**

   * *Type*: Float
   * *Description*: Measured or imputed numeric value for that (`czso_code`, `year`, `metric`).

9. **`unit`**

   * *Type*: String/Category
   * *Description*: Unit of measure, matching the `metric`:

     * `"CZK_avg_gross_monthly_per_fulltime"` for wages.
     * `"ths"` for number of employees.
     * `"2015=100"` for PPI.

10. **`source`**

    * *Type*: String
    * *Description*: Indicates how the row was obtained:

      * **Original** (e.g., `"CZSO"` / `"CZSO – industry"` / `"CZSO – without industry"`) if the value existed in the raw data.
      * **`"PROPAGATED from level X (CODE)"`** if the value was filled in by ascending the NACE hierarchy from a parent code at level `X` (with that parent’s `czso_code` shown in parentheses).

---

### Notes on Data Sources and Transformations

1. **Underlying Inputs**

   * Starts from the tidy file `data_by_nace_annual_tidy.parquet`, which contains only observed values for three metrics (`avg_wages_by_nace`, `no_of_employees_by_nace`, `ppi_by_nace`) at various NACE levels.
   * Uses the NACE hierarchy table (`t_nace_matching.parquet`) to know each code’s parent at levels 1 through 5.

2. **Propagation Logic**

   * **Full grid creation**: For each combination of NACE code (from the hierarchy), year (2000–2024), and metric, the algorithm builds a “complete” row set.
   * **Identify missing**: Any (`czso_code`, `year`, `metric`) with no original value in the raw dataset is flagged.
   * **Recursive search**: For each missing point, the script checks its immediate parent code (level – 1) in the hierarchy; if that parent has a non‐missing value for the same year/metric, it is copied down. If that parent is also missing, the search continues up one more level, and so on, until either a non‐missing value is found or the top of the hierarchy is reached.
   * **Umbrella fallback**: If none of the direct ancestors carry a value, the algorithm can propagate from a higher‐level aggregate (e.g., `"B+C+D+E"` for any industrial division in B, C, D, or E). In practice, any level‐0 code already had its values “expanded” to individual divisions before propagation, so most missing entries at level 1 or 2 will be filled from their closest ancestor or from the umbrella code if present.
   * **Tagging**: Each imputed row’s `source` column is set to `"PROPAGATED from level X (PARENT_CODE)"` to record which code/level supplied the value.

3. **Final Cleanup**

   * Any rows whose `czso_code` does not appear in the NACE hierarchy are dropped.
   * The final table is merged (left‐join) with `t_nace_matching.parquet` to add the `magnus_nace` mapping.
   * The result is saved to `data_by_nace_annual_tidy_propagated.parquet`.

4. **Usage**

   * Downstream analysis can distinguish “true” observations (where `source` does not contain `"PROPAGATED"`) from imputed ones.
   * Because all codes in the hierarchy now have a row for every year/metric, it is straightforward to compute complete bottom‐up indicators (e.g., aggregate subdivisions back into divisions) without gaps.

By encapsulating both observed and hierarchically imputed values, this propagated dataset ensures that every NACE code has a definitive value for each year and metric, facilitating consistent time‐series analyses across all levels of the classification.

---

## 5. **`magnusweb_tidy.parquet`**

### Purpose
Contains **firm-level** accounting and descriptive data exported from MagnusWeb (`export-7.csv`). The script reshapes the dataset from wide to long format, parsing time-coded columns (e.g., “2023/4Q Hospodářský výsledek před zdaněním”) into `year`, `quarter`, and `metric`.

### Variables and Definitions

1. **`ico`**  
   - *Type*: String  
   - *Description*: The firm’s identification number (IČO).

2. **`name`**  
   - *Type*: String  
   - *Description*: The firm’s name (Název subjektu).

3. **`main_nace`** / **`main_nace_code`**  
   - *Type*: Category (textual description) / String (code)
   - *Description*: The main NACE activity (description and code).  

4. **`sub_nace_cz`** / **`sub_nace_cz_code`**  
   - *Type*: Category/String  
   - *Description*: Additional (secondary) NACE activity (description and code). May be missing.

5. **`main_okec`** / **`main_okec_code`**  
   - *Type*: Category/String  
   - *Description*: OKEČ classification (the predecessor to NACE in CZ). May be missing.

6. **`sub_okec`** / **`sub_okec_code`**  
   - *Type*: Category/String  
   - *Description*: Additional OKEČ classification, if available.

7. **`esa2010`** / **`esa95`**  
   - *Type*: Category  
   - *Description*: Firm’s institutional sector classification under ESA 2010 / ESA 95, if provided.

8. **`locality`** / **`region`**  
   - *Type*: Category  
   - *Description*: Geographical location (e.g., city/district) and higher-level region.

9. **`num_employees`**  
   - *Type*: Integer (nullable)  
   - *Description*: Stated number of employees.

10. **`turnover_cat`**  
   - *Type*: Category  
   - *Description*: Category of turnover (e.g., 500 000 000 - 999 999 999 Kč).

11. **`audit`**  
   - *Type*: Category  
   - *Possible values*: `"Yes"`, `"No"`, or missing.  
   - *Description*: Indicates whether the firm undergoes statutory audit.

12. **`consolidation`**  
   - *Type*: Category  
   - *Possible values*: `"Yes"`, `"No"`, or missing.  
   - *Description*: Indicates whether the firm’s statements are consolidated.

13. **`currency`**  
   - *Type*: Category  
   - *Possible values*: `"CZK"`, `"EUR"`, or missing.  
   - *Description*: Currency used for the firm’s financial statements in the source.

14. **`date_founded`** / **`date_dissolved`**  
   - *Type*: Date (YYYY-MM-DD)  
   - *Description*: Registration date and dissolution date (if dissolved). May be missing.

15. **`year`**  
   - *Type*: Integer (nullable)  
   - *Description*: Reporting year for the melted accounting/financial data.

16. **`quarter`**  
   - *Type*: Integer (nullable)  
   - *Description*: Reporting quarter (1–4). If annual-only data, this may be `NaN`.

17. **`metric`**  
   - *Type*: Category/String  
   - *Description*: Type of financial statement item or indicator. Key mappings include:
     - `profit_pre_tax` (Hospodářský výsledek před zdaněním)  
     - `profit_net` (Hospodářský výsledek za účetní období)  
     - `oper_profit` (Provozní hospodářský výsledek)  
     - `costs` (Náklady)  
     - `sales_revenue` (Obrat / Výnosy / Tržby)  
     - `turnover` (Tržby, Výkony)  
     - `total_assets` (Aktiva celkem)  
     - `fixed_assets` (Stálá aktiva)  
     - `current_assets` (Oběžná aktiva)  
     - `other_assets` (Ostatní aktiva)  
     - `total_liabilities` (Pasiva celkem)  
     - `equity` (Vlastní kapitál)  
     - `debt` (Cizí zdroje)  
     - `other_liabilities` (Ostatní pasiva)

18. **`value`**  
   - *Type*: Float  
   - *Description*: The numeric figure for the chosen `metric`. Units may be in thousands or full currency units, depending on the original source. Check `currency` to see if it is CZK or EUR.

### Notes
- Each row represents a single metric for a firm in a given year/quarter.  
- If the original column did not contain quarter information, `quarter` is left empty (`NaN`).
- Some firms or rows may have missing data in `value` for certain periods.

---


## 6. **`t_nace_matching.parquet`**

   * *Purpose*: Provides a cleaned, hierarchical mapping of NACE Rev. 2 codes (from CZSO), including both Czech and English short labels, incremental codes at each level, a Eurostat-style “full\_nace” path, a padded Magnus format code, and an industry‐sector indicator. This table underpins all NACE‐based joins and propagation.

2. **Variables (Columns) and Data Types**

   1. **`name_czso_cs`** *(string)*

      * Czech short description (abbreviated text) of the NACE item.
   2. **`name_czso_en`** *(string)*

      * English short description, imported from the CZSO English CSV. 
   3. **`level`** *(integer)*

      * Hierarchy depth in NACE:

        * `1` = top (letter)
        * `2`–`5` = successive numeric subdivisions
   4. **`czso_code`** *(string)*

      * Raw CZSO code (`chodnota`), e.g.

        * Level 1: single letter (“A”, “B”, …)
        * Level 2+: full numeric strings (e.g. “011”, “0111”).
   5. **`level1_code`** *(string)*

      * Top-level letter (same for all descendants under that branch).
   6. **`level2_code`** *(string)*

      * Incremental code at NACE Level 2: the full numeric code (e.g. “011”). Empty if the record is Level 1.
   7. **`level3_code`** *(string)*

      * Incremental code at NACE Level 3: the suffix beyond its parent’s Level 2. Empty for levels < 3.
   8. **`level4_code`** *(string)*

      * Incremental code at NACE Level 4: suffix beyond Level 3. Empty for levels < 4.
   9. **`level5_code`** *(string)*

      * Incremental code at NACE Level 5: suffix beyond Level 4. Empty for levels < 5.
   10. **`full_nace`** *(string)*

       * Compact hierarchical string in Eurostat style, constructed as `<letter>.<inc2>.<inc3>.<inc4>.<inc5>` (e.g. “A.01.1.1.10”). Always starts with the Level 1 letter, followed by each incremental piece.
   11. **`magnus_nace`** *(string)*

       * Six-digit numeric code (padded with trailing zeros) for NACE Levels 2–4. For Level 1, it’s simply the letter. For Level 5, left empty (Magnus format does not use that depth).
   12. **`industry_flag`** *(boolean)*

       * `True` if the Level 1 letter is in {B, C, D, E}, indicating an industrial sector. Otherwise `False`. - note: currently obsolete, may be removed.

3. **Possible Values / Definitions**

   * **`name_czso_cs`**: CZSO’s Czech abbreviation (e.g., “Zemědělství” might appear for code “A”).
   * **`name_czso_en`**: CZSO’s English abbreviation; if no English row existed, this remains `""`.
   * **`level`**:

     * `1` = NACE section (letter).
     * `2` = two- or three-digit division (e.g., “011”).
     * `3`–`5` = deeper NACE subclasses (if present in the official CZSO file).
   * **`czso_code`**: The raw code string exactly as provided by CZSO.
   * **`level1_code`**: A letter (“A”–“U”); same for the entire branch.
   * **`level2_code`**: Full numeric at Level 2 (e.g., “01” or “011”), empty for Level 1.
   * **`level3_code`**, **`level4_code`**, **`level5_code`**: Only populated when the record’s `level` ≥ 3, 4, 5 respectively. Each is the suffix that differentiates from its parent.
   * **`full_nace`**: A dot-separated string combining `level1_code` and each nonempty incremental code:

     * Example: For a record with `letter = “C”` and numeric lineage (“10”, “105”, “1051”, “10510”), the `inc_codes` would be `[“10”, “5”, “1”, “0”]`, so `full_nace = "C.10.5.1.0"`.
   * **`magnus_nace`**:

     * If `level` is 1: equals `level1_code` (letter).
     * If `level` is 2–4: pad `czso_code` to length 6 with trailing zeros (e.g., “105” → “105000”).
     * If `level` is 5: left as `""`.
   * **`industry_flag`**: True if `level1_code` in {B, C, D, E}, else False.

4. **Notes on Data Sources and Transformations**

   * **Original Input**:

     * CZSO’s NACE Rev. 2 classification CSV (`KLAS80004_CS_NACE_classification.csv` for Czech labels, `KLAS80004_EN_NACE_classification.csv` for English labels). Each row had these columns:

       1. `uroven` (level),
       2. `chodnota` (code),
       3. `zkrtext` (short name),
       4. `nadvaz` (parent pointer), plus other metadata.
   * **Ancestry Extraction**:

     * For every row, follow `nadvaz` iteratively to build a reversed list of `(uroven, chodnota)` from Level 1 down to the current row.
   * **Incremental Codes**:

     * Identify the top letter (`level1_code`) from the first ancestor.
     * Collect each numeric code at levels 2+. For the first numeric level, store the entire code. For subsequent numeric levels, remove the parent’s full code prefix to get the “incremental” portion.
   * **`full_nace` Construction**:

     * Join `[level1_code] + incremental_codes` with dots (`.`). Even if some numeric levels are missing, the string concatenation always reflects the actual path.
   * **`magnus_nace` Computation**:

     * If `level ∈ {2,3,4}`, right-pad `czso_code` to length 6 with zeros.
     * If `level = 1`, set to `level1_code` itself.
     * If `level = 5`, leave empty (Magnus format does not include 5th level).
   * **`industry_flag`**:

     * Set to `True` when `level1_code` ∈ {“B”, “C”, “D”, “E”}, else `False`.
   * **English Label Enrichment**:

     * Loaded the EN CSV, matched on `chodnota`, and filled `name_czso_en`. If no match, left as empty string.
   * **Final Cleanup & Output**:

     * Reordered columns so that `name_czso_en` appears immediately after `name_czso_cs`.
     * Saved the DataFrame as Parquet (`t_nace_matching.parquet`) for downstream joins with data\_by\_nace tables.
   * **Usage**:

     * This table supplies every NACE code’s lineage (via `levelX_code` and `full_nace`), a universally padded “magnus” code for matching MagnusWeb firm data, and a quick industry indicator. All propagation or roll-up logic relies on these parent pointers and incremental codes.
