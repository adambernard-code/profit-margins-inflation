
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
     - `hicp_dec`: HICP Overall Index for December (index base can vary by ECB standards; it represents the end-of-year price level).  
     - `nom_gr_avg_wage_czk`: Average nominal gross monthly wage in CZK (per full-time equivalent), from CZSO.  
     - `no_of_employees_ths`: Number of employees in thousands, from CZSO data.  
     - `gdp_nominal_prices`: Nominal GDP (usually in CZK millions), from CZSO.  
     - `gdp_2020_base_prices`: Real GDP in constant 2020 prices (CZK millions), from CZSO.  
     - `gdp_2020_base_prices_sopr`: Year-over-year index/volume change (SOPR) in 2020 prices, from CZSO (if present, typically an index or percent).  
     - `deflator_nominal`: GDP deflator (index or ratio), from CZSO.  
     - `deflator_base_2020`: An additional GDP deflator variant with 2020 as the base year, from CZSO.  
     - `unemp_rate`: Unemployment rate (percent), from CZSO.  
     - `fx_czk_eur_annual_avg`: Average annual exchange rate (CZK per EUR), from CNB.  

3. **`value`**  
   - *Type*: Float  
   - *Description*: The numeric value of the chosen `metric` for the given `year`. Units and meaning depend on `metric`.

### Notes
- All data is annual, covering roughly 2000 to 2024 (depending on availability).  
- Data sources include CNB, CZSO, and ECB (for HICP).
- The dataset is **long/tidy**: each row is a single time-series observation.

---

## 2. **`data_by_nace_annual_tidy.parquet`**

### Purpose
This file collates annual indicators **by NACE code** (or grouped industrial codes). It combines:

- **PPI by NACE** (Producer Price Index for industrial sectors, base year 2015 = 100)  
- **Average Wages by NACE** (average gross monthly wages, in CZK)  
- **Number of Employees by NACE** (in thousands)

Data is structured by year and NACE classification.

### Variables and Definitions

1. **`czso_code`**  
   - *Type*: String  
   - *Description*: NACE or NACE-like code as used by CZSO. Special case: `"industry"` aggregates B+C+D+E.  
     - Example codes: `"industry"`, `"B"`, `"C"`, `"D"`, `"E"`, etc.

2. **`level`**  
   - *Type*: Integer  
   - *Description*: A quick categorization of the detail level.  
     - `0` = Overall industry aggregate (`"industry"`)  
     - `1` = Single-letter or basic NACE division  

3. **`name_cs`**  
   - *Type*: String  
   - *Description*: Czech name or label for the NACE code.  

4. **`name_en`**  
   - *Type*: String  
   - *Description*: English name or label for the NACE code (if provided).  

5. **`year`**  
   - *Type*: Integer  
   - *Description*: Calendar year (~2000–2024).  

6. **`metric`**  
   - *Type*: String  
   - *Description*: Indicator name:
     - `ppi_by_nace_industrial`: Producer Price Index (2015=100) for industrial (B, C, D, E).  
     - `avg_wages_by_nace`: Average gross monthly wage (CZK per full-time) by activity code.  
     - `no_of_employees_by_nace`: Number of employees (in thousands) by activity code.

7. **`value`**  
   - *Type*: Float  
   - *Description*: The numeric value of the `metric` for that `czso_code` and `year`.

8. **`unit`**  
   - *Type*: String  
   - *Description*: Unit of measurement:
     - `2015=100` for `ppi_by_nace_industrial`  
     - `CZK_avg_gross_monthly_per_fulltime` for `avg_wages_by_nace`  
     - `ths` for `no_of_employees_by_nace`  

9. **`source`**  
   - *Type*: String (always `"CZSO"`)  
   - *Description*: Data source reference (Czech Statistical Office).

### Notes
- The data is **annual**. Where original source had quarterly detail, the script aggregates or averages to the yearly level (e.g., Q1–Q4).
- Additional NACE levels (like deeper subdivisions) can be integrated similarly if available.

---

## 3. **`magnusweb_tidy.parquet`**

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
   - *Type*: Category/String  
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
   - *Description*: Category of turnover (e.g., small, medium, large range). Exact meaning from MagnusWeb definitions.

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
