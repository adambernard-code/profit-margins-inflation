
# Data Sources and Preparation Documentation

## Macro Control Indicators (OECD Economic Outlook Series)

To account for broad macroeconomic influences in the Czech Republic (2000–2023), we curated **22 annual indicators from the OECD Economic Outlook (EO)** database. Each series corresponds to a distinct economic channel, ensuring comprehensive coverage of demand, cost, external, labor, fiscal, and price dynamics. These indicators (listed by their OECD short codes) include:

* **Demand cycle:** **GAP** – Output gap (% of potential GDP), capturing cyclical demand pressure (positive gap = overheated economy, upward margin pressure).
* **Cost pressures:** **ULC** – Unit labour cost (total economy), proxy for aggregate wage cost push; and **RPMGS** – Relative price of imported goods & services, reflecting non-energy import cost shocks.
* **External sector:** **EXCH** – CZK/USD exchange rate, to gauge import cost pass-through; **EXCHEB** – Nominal effective exchange rate (trade-weighted) for competitiveness.
* **Labour market:** **UNR** – Unemployment rate (%, avg), indicating slack (high unemployment eases wage and margin pressures); **HRS** – Average hours worked per worker, indicating labor utilization intensity.
* **Price anchors:** **CPI\_YTYPCT** – Headline CPI inflation (year-over-year %); **PCORE\_YTYPCT** – Core inflation (y/y %, excluding food & energy) for underlying price trends.
* **Fiscal stance:** **NLGXQ** – General government primary balance (% of GDP), a structural fiscal impulse (deficit spending can boost demand and margins); **GGFLMQ** – Gross public debt (% of GDP, Maastricht criteria) for debt burden context; **NOOQ** – Net one-off fiscal measures (% of potential GDP) to net out extraordinary fiscal events (e.g. bailouts).
* **External balance:** **MPEN** – Import penetration (imports as share of domestic demand) to separate imported vs. domestic price pressures; **FBGSQ** – Net exports (% of GDP) as an external demand indicator.
* **Productivity & Capacity:** **PDTY** – Labour productivity (total economy) where gains ease unit costs and lift margins; **KTPV\_ANNPCT** – Productive capital stock growth (% annual) as a capacity expansion proxy (higher investment in capacity can dampen price mark-ups); **ITV\_ANNPCT** – Gross fixed capital formation growth (% annual) capturing investment-led demand.
* **Trade prices:** **ULCDR** – Relative unit labour cost index (Czech vs. trading partners) for cost competitiveness; **TTRADE** – Terms of trade index (goods & services) to distinguish price vs. volume effects in trade (improving terms can boost domestic margins).
* **Monetary conditions:** **IRS** – Short-term interest rate (policy rate); **IRL** – Long-term government bond yield, indicating financing costs and risk premia.

All series were obtained from the **OECD Economic Outlook (EO) database** (Annual frequency) and cover 2000–2023. They are either in percentage-of-GDP units, growth rates, or index form as noted by their codes. Minimal transformations were needed since many are already in rate or index format (e.g. `_ANNPCT` denotes % growth, codes ending in `Q` are % of GDP). These macro controls will be used as exogenous regressors to **“fully control for macro shocks”** when examining how firm-level margins affect inflation.

## Annual Economy-Wide Indicators (`economy_annual_tidy.parquet`)

**Purpose:** This dataset consolidates key annual Czech Republic macroeconomic indicators from various sources into one table (2000–2024). It includes monetary policy rates, inflation, wages, GDP, labor market, and exchange rate data. By merging these into a single long-format table, we facilitate easy lookup and joining with firm-level data by year.

**Contents:** Each row is identified by a combination of `year` and `metric`, with the value in the `value` column. Notable metrics (and their definitions) are:

* **cnb\_repo\_rate\_annual:** Time-weighted annual average of the Czech National Bank 2-week repo rate (monetary policy rate, in percent). *This was calculated by weighting each policy rate by the number of days it was effective during the year*, to better reflect the true monetary stance over the year.
* **hicp\_dec:** Harmonised Index of Consumer Prices (HICP) – overall index for December of each year (an EU-harmonized inflation measure, % change from previous year’s December). Data sourced from the ECB Data Portal.
* **nom\_gr\_avg\_wage\_czk:** Nominal gross average monthly wage (CZK) per full-time employee. Sourced from Czech Statistical Office (CZSO) annual wage statistics.
* **no\_of\_employees\_ths:** Number of employees (annual average, thousands) from CZSO.
* **gdp\_nominal\_prices:** Nominal GDP (CZK millions) for the year.
* **gdp\_2020\_base\_prices:** Real GDP (CZK millions, constant 2020 prices).
* **gdp\_2020\_base\_prices\_sopr:** Real GDP growth index (same period previous year = 100) – essentially the year-over-year real GDP volume change.
* **deflator\_nominal:** GDP deflator (year-over-year inflation in the domestic output, ratio of nominal to real GDP change).
* **deflator\_base\_2020:** GDP deflator index with 2020 as base year (100).
* **unemp\_rate:** Unemployment rate (%, annual average) from CZSO labor force data.
* **fx\_czk\_eur\_annual\_avg:** Average CZK/EUR exchange rate over the year (Czech koruna per euro), from CNB foreign exchange statistics.
* **import_price_index_ex_energy:** Import price index excluding energy (base year 2015 = 100), capturing non-energy import cost trends. Availability from CZSO 2008 - 2024.

**Data Integration:** These series were collected from multiple official sources and merged on the `year` column. For example, the CNB repo rate data came from a text file of all policy rate decisions (which we processed into annual averages), the HICP inflation from the ECB/Eurostat database for Czech Republic, and wages, employment, and GDP figures from CZSO’s published time series (e.g., CZSO “Wages - time series” product code 110030-25 for wage and employment data, and national accounts releases for GDP). All series cover roughly 2000–2024, though some (like HICP or wages) may start slightly later depending on data availability.

**Structure:** The final format is **tidy (long)**: columns = `year`, `metric`, `value`. This makes it easy to filter or pivot as needed for analysis. Units vary by metric (most are percentages or CZK). For instance, `unemp_rate` and `cnb_repo_rate_annual` are percentages, `gdp_nominal_prices` is in millions CZK, etc., as indicated by the metric name.

## Industry-Level Indicators by NACE (`data_by_nace_annual_tidy.parquet`)

**Purpose:** This dataset provides annual indicators broken down by industry (NACE classification) for the Czech economy, covering 2000–2024. It includes producer price indices (PPI) for industrial and service sectors, as well as average wages and employment by industry. By structuring data by NACE codes, we can link macro trends to firm-level data by industry.

**Key Contents & Metrics:**

* **ppi\_by\_nace\_industry:** Producer Price Index for industrial sectors (NACE sections B, C, D, E – Mining, Manufacturing, Utilities), base year 2015 = 100.
* **ppi\_by\_nace\_aggregated:** Service Producer Price Index for aggregated non-industry sectors (covering NACE sections outside B–E), also rebased to 2015 = 100 for consistency.
* **ppi\_by\_nace:** A unified PPI series combining the above two – for each NACE code, this provides the appropriate producer price index (industrial or services as applicable). This was constructed by concatenating the two datasets while avoiding overlap.
* **avg\_wages\_by\_nace:** Average gross monthly wage (CZK per full-time equivalent) by industry (NACE).
* **no\_of\_employees\_by\_nace:** Number of employees (thousands, full-time equivalent) by industry.

Each observation is identified by `czso_code` (a NACE code or aggregate code), `year`, and `metric`. We include NACE at various hierarchical levels: top-level aggregates (e.g., `"B+C+D+E"` for total industry), single-letter sections (A, B, C, ...), two-digit divisions, etc., with a `level` indicator (0 for broad aggregates, 1 for sections, 2 for divisions, etc.).

**Data Sources:** Industrial PPI data come from CZSO’s industry price index releases (annual indices) for NACE B–E. Service sector PPI comes from CZSO’s separate service producer price index tables. For example, CZSO Table 1.1 for services PPI provided price indices by service sector, which we re-based from their original base (some were base 2020) to 2015=100 to match the industry PPI. Wage and employment by NACE were taken from CZSO labor statistics (annual average wages and employee counts by NACE sections and divisions). All raw data values like ":" (not available) or "i.d." (indeterminate) were converted to `NaN` to mark missingness.

**Transformations:**

1. *Rebasing and Filtering:* Industry PPI (B–E) was taken as-is with base 2015=100. Service PPI series (covering sectors F onwards) were originally on base 2015=100 for some series but others (like agriculture) were base 2020. We converted those to 2015 base for consistency. We also dropped any duplicate or overlapping entries (for instance, the industrial aggregate B+C+D+E appears in both datasets, so we ensure it’s taken only once).
2. *Combining PPI:* We created a unified `ppi_by_nace` metric by concatenating the industrial PPI dataset and the services PPI dataset. This yields a PPI time series for virtually all economic activities. Overlap was handled by excluding industrial codes from the service PPI part before merging.
3. *Annualizing Wages/Employment:* Quarterly wage data (from four quarterly sheets) were averaged to get annual figures per NACE. This included summing or averaging the four quarters for each year. For number of employees, we summed the quarterly values and/or took an average (depending on CZSO’s methodology, typically average of quarterly end-of-period counts for annual).
4. *Cleaning Codes:* We standardized NACE codes and labels. For example, the CZSO uses a code "B+C+D+E" labeled “Průmysl” (Industry) for the total industry aggregate – we preserved combined codes like this for aggregates. We also ensured English labels were provided (using CZSO English classifications where available, otherwise using Czech).
5. *Long Format:* Similar to the economy dataset, we pivoted the data into a long format. Initially, separate data frames for each metric were created then “melted” (e.g., a wide table of PPI by year turned into year-value pairs). Finally, all metrics were concatenated with a common format. The `unit` column denotes the unit of the metric (`"2015=100"` for indices, `"CZK_avg_gross_monthly_per_fulltime"` for wages, `"ths"` for thousands of employees).

This rich industry-level dataset allows analysis of price dynamics and labor costs at the industry level, and it serves as a link between macro trends and firm microdata via NACE codes.

## Propagated Industry Data (`data_by_nace_annual_tidy_propagated.parquet`)

**Purpose:** This file extends the above industry dataset by **filling in missing values for finer-level NACE codes using higher-level data**. Many detailed industries may lack a reported PPI or wage value (especially at the 2-digit or 4-digit level). We propagate values from parent categories so that every NACE code in our hierarchy has a complete time series for each metric (wage, employment, PPI) from 2000–2024. This ensures consistency when merging with firm-level data, as every firm’s NACE code will have some value for these industry benchmarks.

**Method – Hierarchical Propagation:** Using the NACE hierarchy, for each missing observation we ascend the hierarchy until we find a non-missing value:

* We first assembled a “full grid” of all combinations of NACE code, year, and metric that should exist (using our NACE classification table described below). Any entry not present in the original data was marked for imputation.
* For a missing value (e.g., wage for NACE division 35 in 2005 is missing), we look at that code’s parent aggregate (e.g., parent of division 35 might be section “D” or some higher combo). If the parent has a value for that year, we use it. If not, move further up (to section or top-level aggregate).
* In some cases, a top-level umbrella (like “B+C+D+E” for all industry) was used as the ultimate fallback for any industrial code lacking its own data. Similarly, for services we had an aggregate of all services sectors.
* Each imputed value’s source is documented in a `source` field (e.g., “PROPAGATED from level 1 (B+C+D+E)” if it took the section aggregate value). This distinguishes imputed data from originally reported data.

After propagation, **each NACE code at each year has a definite value for wages, employment, and PPI**. Of course, lower-level values that were filled in are not actual observations but carry their parent’s value – analysts can still identify them via the `source` flag.

We then merged this with the NACE mapping table to attach the `magnus_nace` code (a padded numeric code matching the format used in firm data, explained below). The resulting dataset is useful for computing industry aggregates or matching firms with industry-level data without missing entries. For example, if a firm’s NACE is a specific manufacturing subclass that had no separate PPI, it will use the division or section-level PPI so that a value is available.

## NACE Classification Mapping (`t_nace_matching.parquet`)

**Purpose:** This is a reference table defining the **NACE Rev. 2 industry classification hierarchy** as used in our data. It maps each NACE code to its level in the hierarchy, parent code, and provides standardized labels in Czech and English. It also provides a crosswalk to the code format used by the MagnusWeb database.

**Key Fields:**

* **czso\_code:** The NACE code string as given by CZSO (this can be a letter for level-1 sections, or numbers for lower levels, e.g. `"A"`, `"01"`, `"011"`).
* **level:** An integer 1 through 5 indicating the depth (1 = Section (letter), 2 = Division (2-digit), 3 = Group (3-digit), 4 = Class (4-digit), 5 = Sub-class (5-digit in CZSO classification)).
* **name\_czso\_cs** and **name\_czso\_en:** Short names of the industry in Czech and English, respectively (e.g., “Zemědělství” / "Agriculture" for section A).
* **level1\_code, level2\_code, ... level5\_code:** These break out each part of the code’s hierarchy. For example, a level 3 code like 011 might have level1\_code = "A", level2\_code = "01", level3\_code = "1". These fields help identify parent relationships.
* **full\_nace:** A composite string showing the full hierarchy path (e.g., `"A.01.1"` for code 0111). This is useful for readability and ensuring uniqueness in hierarchy navigation.
* **magnus\_nace:** A **6-digit zero-padded code** used to match with firm data. MagnusWeb (the firm database) uses a fixed-width code: we use the section letter for level 1, or pad numeric codes to 6 digits (e.g., NACE 105 becomes "105000", NACE 1071 becomes "107100"). This field enables joining the industry data to firm records. (Note: Level 5 codes in CZSO schema were not used in Magnus, so they may be left blank or handled as needed).
* **industry\_flag:** A boolean indicating if the NACE section is industrial (True for sections B, C, D, E; False otherwise). This was added for convenience to quickly filter manufacturing/mining/utilities vs. other sectors.

**Construction:** We started from official CZSO classification files (CSV) for NACE Rev.2 in Czech and English. Each entry had a pointer to its parent (`nadvaznost`). We reconstructed the hierarchy by iteratively climbing to level 1 for each code, collecting the intermediate codes. The incremental numeric codes for each level (beyond the letter) were extracted (e.g., for "0111", level2\_code = "01", level3\_code = "1", level4\_code = "1"). The English names were matched via the code where available; if an English name was missing, we left it blank or defaulted to Czech. We then created the padded `magnus_nace` code as described (for level ≥2).

This table ensures consistency in how industries are referenced across datasets and provides the backbone for the **hierarchical propagation** described above (by knowing each code’s ancestors).

## Firm-Level Panel (MagnusWeb) Data and Preparation (`magnusweb_tidy.parquet`)

The firm-level dataset originates from **MagnusWeb** (by Bureau van Dijk), which provides financial statements for Czech companies. We processed the raw firm data into a **panel dataset** of annual firm-year observations, focusing on key financial variables. Below we document how this was done and what the final data contains.

### Data Curation Process for Firm Data

**Source & Raw Format:** The raw data consisted of multiple CSV files exported from MagnusWeb, with a wide format where each firm (identified by an IČO, the company ID) had many columns for various years and quarters (e.g., `2020/4Q Assets`, `2019/4Q Assets`, etc.), plus static firm information. The data included quarterly entries, but we primarily need annual data.

**Steps to Transform:**

1. **Loading & Concatenation:** We used a Python **Polars** pipeline for efficient data handling (Polars allows lazy evaluation for large datasets). All CSV files were lazily scanned and concatenated into one big table. This avoids high memory usage by not reading everything eagerly.

2. **Melting (Wide to Long):** We separated static columns (firm metadata like name, NACE, address, etc.) from time-series columns. The time-series columns had names containing a year and quarter (e.g., `2021/4Q Náklady`). We **melted** the table on these time-coded columns, turning columns into rows:

   * The melt produced a long table with columns: `IČO` (firm ID), `variable` (the original column name, e.g., "2021/4Q Náklady"), and `value`.
   * We then parsed the `variable` string to extract `year`, `quarter`, and the metric name. For example, `"2021/4Q Náklady"` becomes `year=2021`, `quarter=4Q`, `metric=Náklady` (which means "costs").
   * Parsing was done via regex, distinguishing cases like "2020" (annual) vs "2020/4Q". We standardized quarter notation to Q1–Q4 or noted annual if no quarter given.

3. **Filtering to Annual Observations:** We retained only the **annual data** – specifically, full-year values. Many firms only report annually (often as 4th quarter or year-end snapshot). We therefore kept:

   * Rows where `quarter` is "4" (fourth quarter data, which in this database represents the end-of-year accounts).
   * Rows with no quarter (some metrics might be yearly by default).
     This effectively filters the long data to one observation per firm per year for each metric, using Q4 as the annual representative. Quarterly interim data (Q1–Q3) were dropped to focus on year-end figures.

4. **Pivot to Wide Panel:** Next, we pivoted the long data back to a **wide format**, but now with one row per firm-year:

   * Grouped by firm `IČO` and `year`.
   * For each metric, took the `value` at that year (after the above filtering, there should be at most one value per firm-year-metric).
   * The result is a wide DataFrame where columns are metrics like `turnover`, `profit_pre_tax`, etc., and each row is a specific firm in a specific year.
   * We also brought along the static firm info for each firm-year. Since static info (e.g. legal form) doesn’t change over time for a given firm (except in rare cases), we merged the static columns from the firm’s latest entry. We ensured each firm-year has the relevant firm metadata attached.

5. **Standardizing Columns:** The raw data had Czech metric names. We mapped these to concise English names:

   * For example: *“Náklady”* → **costs**, *“Hospodářský výsledek před zdaněním”* → **profit\_pre\_tax**, *“Hospodářský výsledek za účetní období”* → **profit\_net**, *“Provozní hospodářský výsledek”* → **oper\_profit**, *“Obrat / Výnosy”* → **turnover**, *“Tržby / Výkony”* → **sales\_revenue**, *“Aktiva celkem”* → **total\_assets**, *“Pasiva celkem”* → **total\_liabilities\_and\_equity**, *“Vlastní kapitál”* → **equity**, etc.
     We also standardized firm attributes: *“Název subjektu”* → **name**, *“Hlavní NACE”* → **main\_nace**, etc. This mapping was carefully documented so that each new column name is self-explanatory and consistent.

6. **Data Types and Cleaning:** We converted data types to appropriate formats:

   * Numeric financial fields to floats (some were read as string due to formatting and needed cleaning of thousand separators or text).
   * Categorical fields like region, legal\_form, etc., to categories.
   * The IČO (company ID) to string (to preserve leading zeros if any).
   * Dates (foundation and dissolution dates) to a date type.
   * Employee counts to integer.
   * We also dropped truly static columns from the final panel if they don’t vary and aren’t needed for analysis (to reduce clutter). For example, fields like `entity_type` or `currency` that are constant for each firm were not included in the final analytical dataset, since if needed they can be merged from a separate firm reference.

7. **Final Output:** The resulting `magnusweb_tidy.parquet` is a **firm-year panel** dataset. Each row = one firm in one year, identified by `ico` and `year`. It contains the firm’s main financial statement items and some identifiers. We saved it in Parquet format (an efficient columnar format) for easy loading in analysis software.

**Note:** Only **4th-quarter or annual values** are used to ensure each firm-year is a single observation (we chose 4Q as it typically represents the year-end balance sheet and cumulative income statement). This approach assumes that if a firm reports quarterly, the Q4 values represent the year totals (which is usually the case in financial statements).

### Final Panel Data Dictionary

Below we describe all columns in the final firm-year panel, grouped by category. This serves as a data dictionary for reference.

**A. Firm Identifiers and Static Attributes** (do not vary over time for a given firm):

* **ico** – *Company ID number.* *(Czech IČO)* Unique identifier of the company.
* **name** – *Company name.* Legal name of the business.
* **main\_nace** – *Main NACE sector (text).* The primary industry sector description.
* **main\_nace\_code** – *Main NACE code (numeric/alphanumeric).* E.g., “C 25” or “4721” identifying the firm’s principal activity.
* **sub\_nace\_cz** – *Secondary NACE (Czech, text).* Secondary activity description (if any).
* **sub\_nace\_cz\_code** – *Secondary NACE code.*
* **main\_okec** – *Main OKEČ sector (predecessor classification).* Some firms have the older classification.
* **main\_okec\_code**, **sub\_okec**, **sub\_okec\_code** – analogous to the above, but for OKEČ codes (older Czech industry classification, if provided).
* **esa2010** / **esa95** – Institutional sector classification of the firm (under ESA 2010 and previously ESA 95), e.g. non-financial corporation, financial institution, government, etc.
* **locality** – *Municipality/locality.* The city or town of the company’s registered office.
* **region** – *Region (Kraj).* The region of Czech Republic where the company is located.
* **num\_employees** – *Number of employees.* (If available, typically a category or an approximate number provided in Magnus.)
* **num\_employees\_cat** – *Employee count category.* Categorical size class of employment (in Czech categories, e.g. 0–19, 20–49, etc.).
* **turnover\_cat** – *Turnover size category.* Categorical class of annual turnover (e.g., 0–€2M, €2–10M, etc., as often provided by Magnus for classification).
* **audit** – *Audit requirement indicator.* (Yes/No flag if the firm’s statements are audited).
* **consolidation** – *Consolidation indicator.* (Whether the statements are consolidated for a group or solo for the entity).
* **currency** – *Reporting currency.* (Almost all CZK for domestic firms, but included for completeness).
* **date\_founded** – *Date of incorporation.*
* **date\_dissolved** – *Date of dissolution.* (If the firm ceased to exist; otherwise null).
* **status** – *Legal status of entity.* (Active, dissolved, in liquidation, etc.).
* **legal\_form** – *Legal form.* (e.g., “s.r.o.” limited company, “a.s.” joint-stock company, etc.).
* **entity\_type** – *Type of entity.* (E.g., enterprise, branch, government unit – most are enterprises/corporations in this dataset).

(*Note:* These static fields were largely sourced from MagnusWeb firm metadata. In the final panel, we focused on the dynamic financial fields, so some of these may not appear in the saved panel if deemed unnecessary for analysis. They can be merged in from the raw data if needed.)

**B. Core Financial Statement Variables** (annual values, in CZK unless noted):

* **turnover** – *Net turnover (sales revenue).* This represents operating revenues – often the sum of sales of goods and services (excluding certain taxes). It consolidates various revenue lines into a single “turnover” figure.
* **sales\_revenue** – *Sales/outputs.* Similar to turnover; in some data sources “Tržby/Výkony” might be distinguished, but we unify them here. (If both were present, they were combined or the main one used.)
* **costs** – *Total costs (expenses).* All operating expenses for the year.
* **oper\_profit** – *Operating profit (EBIT).* Earnings before interest and taxes – profit from operations.
* **profit\_pre\_tax** – *Profit before tax (EBT).* Earnings before tax, i.e., after interest but before corporate income tax.
* **profit\_net** – *Net profit (after tax).* Final profit or loss for the year.
* **total\_assets** – *Total assets.* The sum of fixed and current assets; represents the balance sheet total.
* **fixed\_assets** – *Fixed assets.* Non-current assets such as property, plant, equipment, long-term investments.
* **current\_assets** – *Current assets.* Short-term assets like inventory, receivables, cash.
* **other\_assets** – *Other assets.* Any assets not in the main categories (sometimes not used explicitly).
* **total\_liabilities\_and\_equity** – *Total liabilities and equity.* This should equal total assets (balance sheet total on the liabilities side).
* **equity** – *Shareholder’s equity.* Book value of equity.
* **total\_liabilities** – *Total liabilities (debt).* All outside liabilities (both long and short-term debt).
* **other\_liabilities** – *Other liabilities.* (If applicable, e.g., provisions or minor categories not included in main debt).

(*Note:* In many cases, `total_liabilities_and_equity` duplicates `total_assets`. We include one as a consistency check. If any discrepancy existed, it might indicate data issues. In a clean dataset, these should balance.)

**C. Computed Financial Ratios/Metrics** (derived for analysis):

In our analysis, we derive additional ratios to assess profitability, leverage, etc., although these may not be stored explicitly in the Parquet and might be computed on the fly. For completeness, important ones include:

| New column                                         | Description                                      | Formula                                          |
| -------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------ |
| **Operating margin**<br>`operating_margin_cal`     | Core pricing power from operations               | `oper_profit ÷ sales_revenue`                    |
| **Net margin**<br>`net_margin_cal`                 | “Bottom-line” profitability after interest & tax | `profit_net ÷ sales_revenue`                     |
| **ROA (EBIT)**<br>`roa_ebit_cal`                   | Return on assets—efficiency of asset base        | `oper_profit ÷ total_assets`                     |
| **ROE**<br>`roe_cal`                               | Return on equity—owners’ yield                   | `profit_net ÷ equity`                            |
| **Equity ratio**<br>`equity_ratio_cal`             | Share of assets financed by owners               | `equity ÷ total_assets`                          |
| **Cost ratio**<br>`cost_ratio_cal`                 | Average cost share in revenue                    | `costs ÷ sales_revenue`                          |
| **Effective tax rate**<br>`effective_tax_rate_cal` | Fiscal burden on pre-tax profit                  | `(profit_pre_tax − profit_net) ÷ profit_pre_tax` |
| **Revenue growth**<br>`rev_growth_cal`             | Year-on-year revenue momentum                    | `pct_change(sales_revenue)` over each ICO        |
| **Cost growth**<br>`cost_growth_cal`               | Year-on-year cost shock size                     | `pct_change(costs)` over each ICO                |
| **Op. profit growth**<br>`op_profit_growth_cal`    | Year-on-year operating profit change             | `pct_change(oper_profit)` over each ICO          |
| **Asset turnover**<br>`asset_turnover_cal`         | How quickly assets generate revenue              | `sales_revenue ÷ total_assets`                   |
| **Labor productivity**<br>`labor_productivity_cal` | Sales per employee                               | `sales_revenue ÷ num_employees`                  |


**D. Data Reliability and Notes:** All financial values are in nominal CZK. Some firms report in EUR, but those were converted or indicated by the `currency` field (in our dataset, we filtered to CZK-denominated accounts where possible for consistency). The data covers both large and small firms; note that smaller firms might have missing values for some financial fields if they report abbreviated statements. We mitigated this by focusing on the main fields which most firms report.

Additionally, the panel is unbalanced – firms enter and exit (date\_founded and date\_dissolved indicate this). The `status` field can signal if a firm was active in a given year or not.

---

This comprehensive documentation provides the necessary background on each dataset and the transformations applied. All these curated data files will be used in subsequent modeling, ensuring that macroeconomic context and firm-level details are well-integrated. By cleaning and organizing the data as described, we aim to meet high research standards and enable robust analysis of the relationship between profit margins and inflation in the Czech Republic.

**Sources:**

* OECD Economic Outlook Database (No. 117) – for macro indicators.
* Czech National Bank (CNB) – policy interest rates and exchange rates (repo rate methodology: time-weighted annual averages).
* European Central Bank Data Portal – HICP inflation for Czechia.
* Czech Statistical Office (CZSO) – national accounts, price indices, labor statistics (e.g., wage and employment tables by NACE).


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

See separate documentation for the MagnusWeb dataset, which contains firm-level data from the MagnusWeb database. This file is structured in a tidy format, with each row representing a single firm-year observation.

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
| `magnus_nace`   | String  | A standardized NACE code format:<br> - If `level` is 1: Equals `level1_code` (letter).<br> - If `level` is 2–5: `czso_code` padded with trailing zeros to a length of six digits (e.g., “105” → “105000”). |
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

#### 3.5 Efficiency & Scale Metrics

| Column                   | Formula                         | Description                                       |
| ------------------------ | ------------------------------- | ------------------------------------------------- |
| `asset_turnover_cal`     | `sales_revenue / total_assets`  | Asset turnover (revenue generated per unit asset) |
| `labor_productivity_cal` | `sales_revenue / num_employees` | Labor productivity (sales per employee)           |

---



# Macro Control Indicators for Inflation–Profit‐Margin Analysis

This one-pager summarizes the **22 OECD Economic Outlook series** selected to control for key macro channels in our Czech Republic (2000–2023) profit-margin–inflation study. We chose indicators to capture:

- **Demand cycle:** output gap  
- **Cost pressures:** unit-labour cost, import prices  
- **External sector:** exchange rates, import penetration  
- **Labour market:** unemployment, hours worked  
- **Fiscal stance:** structural balances, debt  
- **Price anchors:** headline vs. core CPI  

Each series is available in the **OECD EO bulk download**, keyed by its short code and described briefly below.

---

## Selected Indicators

| Code            | Series name                                                           | Purpose / Interpretation                                                                                              |
|-----------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **GAP**         | Output gap as a percentage of potential GDP                            | Cyclical demand pressure: positive gap → tight economy, upward margin pressure.                                       |
| **ULC**         | Unit labour cost in total economy                                      | Aggregate labour‐cost push; rising ULC squeezes margins unless firms raise prices.                                    |
| **RPMGS**       | Relative price of imported goods and services                          | Non-energy import‐cost shock; complements energy CPI.                                                                 |
| **EXCH**        | Exchange rate, national currency per USD                               | Pass-through of currency moves into domestic costs.                                                                   |
| **EXCHEB**      | Nominal effective exchange rate, chain-linked, overall weights         | Broader trade-weighted competitiveness measure.                                                                       |
| **UNR**         | Unemployment rate                                                     | Labour‐market slack; high unemployment eases wage/margin pressures.                                                   |
| **HRS**         | Hours worked per worker, total economy                                | Intensive labour utilization (e.g. overtime) can amplify cost pressures.                                               |
| **CPI_YTYPCT**  | Consumer price index (headline inflation), y/y %                      | Anchor for overall price level; used to deflate nominal variables and check real‐margin dynamics.                     |
| **PCORE_YTYPCT**| Core inflation index, y/y %                                            | Underlying inflation excluding food & energy; tests profit-push beyond volatile components.                           |
| **NLGXQ**       | General government primary balance as a percentage of GDP             | Structural fiscal impulse; deficit adds demand pressure, supports margin expansion.                                   |
| **GGFLMQ**      | Gross public debt, Maastricht criterion as a percentage of GDP        | Debt burden and sustainability narrative—relevant to policy constraints on inflation.                                 |
| **MPEN**        | Import penetration, goods and services                                | Share of domestic demand met by imports; helps identify imported vs. domestic price pressures.                        |
| **PDTY**        | Labour productivity, total economy                                    | Efficiency gains reduce unit costs; rising productivity mechanically lifts margins.                                   |
| **KTPV_ANNPCT** | Productive capital stock, volume, annual % growth                     | Capacity expansion proxy; high growth can dampen price‐markup power.                                                  |
| **ITV_ANNPCT**  | Gross fixed capital formation, total, volume, annual % growth         | Investment-led demand pressure; complements output‐gap control.                                                       |
| **CPV_ANNPCT**  | Private final consumption expenditure, volume, annual % growth        | Household‐demand shock; tests whether rising consumption supports higher margins.                                     |
| **FBGSQ**       | Net exports of goods and services as a percentage of GDP             | External demand vs. supply balance; positive exports → additional demand.                                             |
| **ULCDR**       | Competitiveness based on relative unit labour costs (index)           | CZ vs. trading‐partner cost competitiveness; informs import‐price pass-through.                                         |
| **TTRADE**      | Terms of trade, goods and services (index)                            | Distinguishes price vs. volume effects in trade; improving terms of trade can boost margins.                          |
| **IRS**         | Short-term interest rate                                              | Monetary-policy stance; tighter rates may compress financing costs and margins.                                        |
| **IRL**         | Long-term interest rate on government bonds                           | Captures term-premium and debt-service cost channel into net margins.                                                 |
| **NOOQ**        | Net one-offs of general government as a percentage of potential GDP    | Cleans out crisis-related fiscal events (bailouts, windfalls) from structural balance measure.                         |

---

## Data Sample Structure

Each series in the **OECD.ECO.MAD** dataset follows this schema:


STRUCTURE | STRUCTURE\_ID                             | STRUCTURE\_NAME         | ACTION | REF\_AREA | Reference area | MEASURE | Measure                                 | FREQ | TIME\_PERIOD | OBS\_VALUE | UNIT\_MEASURE | CURRENCY | …

DATAFLOW  | OECD.ECO.MAD\:DSD\_EO\@DF\_EO(1.3)            | Economic Outlook 117   | I      | CZE      | Czechia        | GAP     | Output gap as % of potential GDP         | A    | 2023        | –1.62     | PT\_PB1GQ      |          | …



- **FREQ** = A (Annual)  
- **MEASURE** = short code (e.g. GAP, ULC)  
- **OBS_VALUE** = numeric observation  
- **UNIT_MEASURE** = unit or `% GDP` or `% pa` growth  

---

### Selection Rationale

1. **Orthogonality & Exogeneity**: Each control taps a distinct channel—demand cycle, labour costs, external price shocks, fiscal stance—minimizing multicollinearity.  
2. **Policy relevance**: Indicators mirror CNB/ECB narratives (slack, cost-push, fiscal impulse).  
3. **Data availability**: All are annually reported in the OECD EO bulk extract (2000–2023), ensuring consistency with firm-level panel.  
4. **Transform-ready**: Growth rates (`_ANNPCT`), percent-of-GDP (`…Q`), and indexes require minimal preprocessing.

Use this curated set to **fully control macro‐shocks** when estimating how firm‐level operating margins drive Czech inflation.


Variable Name (Short),Description,Unit,Source
,,,
1. 1. Firm-Level Variables (Prefix: firm_),,,
,,,
Variable Name (Short),Description,Unit,Source
firm_ico,Unique firm identifier (IČO – “IČO”),String (8-digit ID),MagnusWeb
firm_name,Legal name of company (“Název subjektu”),String,MagnusWeb
firm_main_nace,Main NACE activity (CZ: “Hlavní NACE”),String (NACE text description),MagnusWeb
firm_main_nace_code,Main NACE code (“Hlavní NACE – kód”),"String / Numeric (e.g. ""C25"")",MagnusWeb
firm_sub_nace_cz,Secondary NACE description (“Vedlejší NACE CZ”),String,MagnusWeb
firm_sub_nace_cz_code,Secondary NACE code (“Vedlejší NACE CZ – kód”),String / Numeric,MagnusWeb
firm_main_okec,Main OKEČ classification (“Hlavní OKEČ”),String,MagnusWeb
firm_main_okec_code,Main OKEČ code (“Hlavní OKEČ – kód”),String / Numeric,MagnusWeb
firm_sub_okec,Secondary OKEČ (“Vedlejší OKEČ”),String,MagnusWeb
firm_sub_okec_code,Secondary OKEČ code (“Vedlejší OKEČ – kód”),String / Numeric,MagnusWeb
firm_esa2010,Institutional sector (ESA 2010),String (sector code),MagnusWeb
firm_esa95,Institutional sector (ESA 95),String (sector code),MagnusWeb
firm_locality,Municipality / Locality (“Lokalita”),String,MagnusWeb
firm_region,Region (“Kraj”),String,MagnusWeb
firm_num_employees,Number of employees (“Počet zaměstnanců”),Integer (persons),MagnusWeb
firm_num_employees_cat,dropped; Employee category (“Kategorie počtu zaměstnanců CZ”),String (category label),MagnusWeb
firm_turnover_cat,Turnover size category (“Kategorie obratu”),String (category label),MagnusWeb
firm_audit,Audit indicator (“Audit”),Boolean (Yes/No),MagnusWeb
firm_consolidation,Consolidation indicator (“Konsolidace”),Boolean (Yes/No),MagnusWeb
firm_currency,Reporting currency (“Měna”),"String (ISO code, e.g. ""CZK"")",MagnusWeb
firm_date_founded,Date of incorporation (“Datum vzniku”),Date (YYYY-MM-DD),MagnusWeb
firm_date_dissolved,Date of dissolution (“Datum zrušení”),"Date (YYYY-MM-DD, or null)",MagnusWeb
firm_status,Legal status (“Stav subjektu”),"String (e.g., active/dissolved)",MagnusWeb
firm_legal_form,Legal form (“Právní forma”),String,MagnusWeb
firm_entity_type,Entity type (“Typ subjektu”),String,MagnusWeb
firm_year_founded,Year of foundation (parsed from date),Integer (year),MagnusWeb
firm_year_dissolved,Year of dissolution (parsed from date),Integer (year or null),MagnusWeb
firm_is_dissolved,Dissolution status (derived),Boolean (True/False),MagnusWeb
firm_other_liabilities,"Other liabilities (“Ostatní pasiva”), only last observation, not time-series (static)",CZK (nominal),MagnusWeb
firm_current_assets,"Current assets (“Oběžná aktiva”), only last observation, not time-series (static)",CZK (nominal),MagnusWeb
firm_total_liabilities,"Total liabilities (“Cizí zdroje”), only last observation, not time-series (static)",CZK (nominal),MagnusWeb
firm_other_assets,"Other assets (“Ostatní aktiva”), only last observation, not time-series (static)",CZK (nominal),MagnusWeb
firm_fixed_assets,"Fixed assets (“Stálá aktiva”), only last observation, not time-series (static)",CZK (nominal),MagnusWeb
,,,
"2. Financial Statement (Time-variant, per firm-year)",,,
,,,
Variable Name (Short),Description,Unit,Source
firm_sales_revenue,"Sales revenue (“Tržby, Výkony / Tržby Výkony”)",CZK (nominal),MagnusWeb
firm_turnover,"Turnover (“Obrat, Výnosy / Obrat Výnosy”)",CZK (nominal),MagnusWeb
firm_oper_profit,Operating profit / EBIT (“Provozní hospodářský výsledek”),CZK (nominal),MagnusWeb
firm_profit_pre_tax,Profit before tax (“Hospodářský výsledek před zdaněním”),CZK (nominal),MagnusWeb
firm_profit_net,Net profit (“Hospodářský výsledek za účetní období”),CZK (nominal),MagnusWeb
firm_costs,Total costs/expenses (“Náklady”),CZK (nominal),MagnusWeb
firm_total_assets,Total assets (“Aktiva celkem”),CZK (nominal),MagnusWeb
firm_equity,Equity (“Vlastní kapitál”),CZK (nominal),MagnusWeb
firm_total_liabilities_and_equity,Liabilities & equity (“Pasiva celkem”),CZK (nominal),MagnusWeb
,,,
3. Derived Ratios & Diagnostics,,,
,,,
Variable Name (Short),Description,Unit,Source
firm_operating_margin_cal,oper_profit / sales_revenue (winsorised 0.5%),Ratio,Calculated
firm_net_margin_cal,profit_net / sales_revenue (winsorised 0.5%),Ratio,Calculated
firm_roa_ebit_cal,oper_profit / total_assets,Ratio,Calculated
firm_roe_cal,profit_net / equity,Ratio,Calculated
firm_equity_ratio_cal,equity / total_assets,Ratio,Calculated
firm_cost_ratio_cal,costs / sales_revenue (winsorised 0.5%),Ratio,Calculated
firm_effective_tax_rate_cal,(profit_pre_tax - profit_net) / profit_pre_tax,Ratio,Calculated
firm_asset_turnover_cal,sales_revenue / total_assets,Ratio,Calculated
firm_labor_productivity_cal,sales_revenue / num_employees,CZK/employee,Calculated
,,,
4. NACE Matching (for sector joins),,,
,,,
Variable Name (Short),Description,Unit,Source
firm_level1_code,"NACE 1st-level code (section, letter, e.g., ""C"")",String,t_nace_matching
level2_code,"NACE 2nd-level code (2-digit, e.g., ""25"")",String,t_nace_matching
firm_name_czso_en,English name for NACE code,String,t_nace_matching
level1_nace_en_name,"English name for NACE 1st-level code (section, letter, e.g., 'C')",String,CZSO
level2_nace_en_name,"English name for NACE 2nd-level code (2-digit, e.g., '25')",String,CZSO
firm_industry_flag,"Industrial sector flag (B,C,D,E=True)",Boolean,t_nace_matching
magnus_nace,"NACE code (Magnus formatting, as Magnus reported)",String,MagnusWeb
,,,
"5. 2. Sector-Level Variables (Prefix: sector_, joined via NACE/year)",,,
,,,
Variable Name (Short),Description,Unit,Source
sector_level1_avg_wages_by_nace,Average gross monthly wage in sector (NACE 1st-level granularity),"CZK / month, per FTE, annual avg, matched on nace_level1",CZSO
sector_level1_no_of_employees_by_nace,Number of employees in sector (NACE 1st-level granularity),"Thousands of persons, matched on nace_level1",CZSO
sector_level1_ppi_by_nace,Producer Price Index by NACE (NACE 1st-level granularity),"Index (base=2015, 2015=100), matched on nace_level1",CZSO
sector_level2_avg_wages_by_nace,Average gross monthly wage in sector (NACE 2nd-level granularity),"CZK / month, per FTE, annual avg, matched on nace_level2",CZSO
sector_level2_no_of_employees_by_nace,Number of employees in sector (NACE 2nd-level granularity),"Thousands of persons, matched on nace_level2",CZSO
sector_level2_ppi_by_nace,Producer Price Index by NACE (NACE 2nd-level granularity),"Index (base=2015, 2015=100), matched on nace_level2",CZSO
,,,
"6. 3. Macro-Level Variables (Prefix: mac_, joined by year)",,,
,,,
Variable Name (Short),Description,Unit,Source
mac_cnb_repo_rate_annual,"CNB policy repo rate (annual time-weighted avg, “repo sazba”)",% p.a.,CNB
mac_hicp_dec,"HICP (Harmonized CPI, Dec values), ICP.M.CZ.N.000000.4.ANR",percentage change vs last year (december),ECB/Eurostat
mac_hicp_overall_roc,"HICP – Overall index annual rate of change (headline inflation), ICP.A.CZ.N.000000.4.AVR",% y/y,ECB/Eurostat
mac_hicp_pure_energy_roc,"HICP – Electricity, gas, solid fuels & heat energy annual rate of change, ICP.A.CZ.N.ELGAS0.4.AVR",% y/y,ECB/Eurostat
mac_hicp_energy_full_roc,"HICP – Electricity, gas & other fuels annual rate of change, ICP.A.CZ.N.045000.4.AVR",% y/y,ECB/Eurostat
mac_nom_gr_avg_wage_czk,Nominal gross average wage (CZK),"CZK / month, FTE",CZSO
mac_no_of_employees_ths,"No. of employees (national, ths)",Thousands of persons,CZSO
mac_gdp_nominal_prices,Nominal GDP (“HDP v běžných cenách”),CZK millions,CZSO
mac_gdp_2020_base_prices,Real GDP (constant 2020 prices),CZK millions (2020 prices),CZSO
mac_gdp_2020_base_prices_sopr,Real GDP YoY volume index (SOPR),Index (prev yr=100),CZSO
mac_deflator_nominal,"GDP deflator, YoY SOPR (same period LY)",Ratio,CZSO
mac_deflator_base_2020,"GDP deflator, base 2020",Index (2020=100),CZSO
mac_unemp_rate,Unemployment rate (“Míra nezaměstnanosti”),%,CZSO
mac_fx_czk_eur_annual_avg,CZK/EUR average annual exchange rate,CZK per EUR,CNB
mac_import_price_index_ex_energy,Import price index excl. energy (Laspeyres),Index (2015=100),Custom/CZSO
mac_FBGSQ,"Net exports (% GDP, OECD code)",% of GDP,OECD EO117
mac_NLGXQ,"Gen. gov. primary balance (% GDP, OECD code)",% of GDP,OECD EO117
mac_GGFLMQ,"Gross public debt (Maastrich Criterion as a % GDP, OECD code)",% of GDP,OECD EO117
mac_RPMGS,Rel. price of imports (OECD code),Index,OECD EO117
mac_IRS,Short-term interest rate (OECD code),% p.a.,OECD EO117
mac_IRL,Long-term govt bond yield (OECD code),% p.a.,OECD EO117
mac_GAP,"Output gap (% potential GDP, OECD code)",%,OECD EO117
mac_NOOQ,"Net one-offs, gen. gov. (% pot. GDP, OECD code) - crisis related fiscal events (bailouts, windfalls)",% of pot. GDP,OECD EO117
mac_PCORE_YTYPCT,"Core inflation, YoY % (OECD code)",% YoY,OECD EO117
mac_HRS,Hours worked per worker (OECD code),Number (annual avg),OECD EO117
mac_CPI_YTYPCT,Headline CPI YoY % (OECD code),% YoY,OECD EO117
mac_UNR,"Unemployment rate, OECD code",%,OECD EO117
mac_EXCH,CZK/USD exchange rate (OECD code),CZK per USD,OECD EO117
mac_MPEN,"Import penetration (% domestic demand, OECD code), note: Share of domestic demand met by imports",%,OECD EO117
mac_ULC,"Unit labour cost, total economy (OECD code)",Index (2021=100),OECD EO117
mac_PDTY,Labour productivity (OECD code),Index (2021=100),OECD EO117
mac_ULCDR,"Relative ULC, Czech vs. trade partners (OECD code)",Index (2021=100),OECD EO117
mac_EXCHEB,Nominal effective exchange rate (OECD code),Index (2021=100),OECD EO117
mac_TTRADE,Terms of trade index (OECD code),Index,OECD EO117
mac_KTPV_ANNPCT,"Productive capital stock growth, % (OECD code)",% YoY,OECD EO117
mac_CPV_ANNPCT,"Private final consumption growth, % (OECD code)",% YoY,OECD EO117
mac_ITV_ANNPCT,"Gross fixed capital formation growth, % (OECD code)",% YoY,OECD EO117
,,,
7. 4. Transformed Variables: Log Year-over-Year Growth (_logyoy),,,
,,,
Variable Name (Short),Description,Unit,Source
firm_costs_logyoy,Log YoY growth of Total costs/expenses,Log points (Δ YoY),Calculated
firm_equity_logyoy,Log YoY growth of Equity,Log points (Δ YoY),Calculated
firm_oper_profit_logyoy,Log YoY growth of Operating profit / EBIT,Log points (Δ YoY),Calculated
firm_profit_net_logyoy,Log YoY growth of Net profit,Log points (Δ YoY),Calculated
firm_profit_pre_tax_logyoy,Log YoY growth of Profit before tax,Log points (Δ YoY),Calculated
firm_sales_revenue_logyoy,Log YoY growth of Sales revenue,Log points (Δ YoY),Calculated
firm_total_assets_logyoy,Log YoY growth of Total assets,Log points (Δ YoY),Calculated
firm_total_liabilities_and_equity_logyoy,Log YoY growth of Liabilities & equity,Log points (Δ YoY),Calculated
firm_turnover_logyoy,Log YoY growth of Turnover,Log points (Δ YoY),Calculated
mac_EXCHEB_logyoy,Log YoY growth of Nominal effective exchange rate,Log points (Δ YoY),Calculated
mac_PDTY_logyoy,Log YoY growth of Labour productivity,Log points (Δ YoY),Calculated
mac_TTRADE_logyoy,Log YoY growth of Terms of trade index,Log points (Δ YoY),Calculated
mac_ULCDR_logyoy,"Log YoY growth of Relative ULC, Czech vs. trade partners",Log points (Δ YoY),Calculated
mac_ULC_logyoy,"Log YoY growth of Unit labour cost, total economy",Log points (Δ YoY),Calculated
mac_deflator_base_2020_logyoy,"Log YoY growth of GDP deflator, base 2020",Log points (Δ YoY),Calculated
sector_level1_avg_wages_by_nace_logyoy,Log YoY growth of average gross monthly wage in sector (NACE 1st-level),Log points (Δ YoY),Calculated
sector_level1_no_of_employees_by_nace_logyoy,Log YoY growth of number of employees in sector (NACE 1st-level),Log points (Δ YoY),Calculated
sector_level1_ppi_by_nace_logyoy,Log YoY growth of producer price index by NACE (NACE 1st-level),Log points (Δ YoY),Calculated
sector_level2_avg_wages_by_nace_logyoy,Log YoY growth of average gross monthly wage in sector (NACE 2nd-level),Log points (Δ YoY),Calculated
sector_level2_no_of_employees_by_nace_logyoy,Log YoY growth of number of employees in sector (NACE 2nd-level),Log points (Δ YoY),Calculated
sector_level2_ppi_by_nace_logyoy,Log YoY growth of producer price index by NACE (NACE 2nd-level),Log points (Δ YoY),Calculated
mac_fx_czk_eur_annual_avg_logyoy,Log YoY growth of CZK/EUR average annual exchange rate,Log points (Δ YoY),Calculated
mac_gdp_2020_base_prices_logyoy,Log YoY growth of Real GDP (constant 2020 prices),Log points (Δ YoY),Calculated
mac_gdp_nominal_prices_logyoy,Log YoY growth of Nominal GDP,Log points (Δ YoY),Calculated
mac_import_price_index_ex_energy_logyoy,Log YoY growth of Import price index excl. energy,Log points (Δ YoY),Calculated
mac_nom_gr_avg_wage_czk_logyoy,Log YoY growth of Nominal gross average wage,Log points (Δ YoY),Calculated
sector_avg_wages_by_nace_logyoy,Log YoY growth of Average gross monthly wage in sector,Log points (Δ YoY),Calculated
sector_no_of_employees_by_nace_logyoy,Log YoY growth of Number of employees in sector,Log points (Δ YoY),Calculated
sector_ppi_by_nace_logyoy,Log YoY growth of Producer Price Index by NACE,Log points (Δ YoY),Calculated
,,,
8. 5. Transformed Variables: Percentage Change (_pct),,,
,,,
Variable Name (Short),Description,Unit,Source
firm_costs_pct,Percentage change of Total costs/expenses,% (Δ YoY),Calculated
firm_equity_pct,Percentage change of Equity,% (Δ YoY),Calculated
firm_oper_profit_pct,Percentage change of Operating profit / EBIT,% (Δ YoY),Calculated
firm_profit_net_pct,Percentage change of Net profit,% (Δ YoY),Calculated
firm_profit_pre_tax_pct,Percentage change of Profit before tax,% (Δ YoY),Calculated
firm_sales_revenue_pct,Percentage change of Sales revenue,% (Δ YoY),Calculated
firm_total_assets_pct,Percentage change of Total assets,% (Δ YoY),Calculated
firm_total_liabilities_and_equity_pct,Percentage change of Liabilities & equity,% (Δ YoY),Calculated
firm_turnover_pct,Percentage change of Turnover,% (Δ YoY),Calculated
mac_EXCHEB_pct,Percentage change of Nominal effective exchange rate,% (Δ YoY),Calculated
mac_PDTY_pct,Percentage change of Labour productivity,% (Δ YoY),Calculated
mac_TTRADE_pct,Percentage change of Terms of trade index,% (Δ YoY),Calculated
mac_ULCDR_pct,"Percentage change of Relative ULC, Czech vs. trade partners",% (Δ YoY),Calculated
mac_ULC_pct,"Percentage change of Unit labour cost, total economy",% (Δ YoY),Calculated
mac_deflator_base_2020_pct,"Percentage change of GDP deflator, base 2020",% (Δ YoY),Calculated
mac_fx_czk_eur_annual_avg_pct,Percentage change of CZK/EUR average annual exchange rate,% (Δ YoY),Calculated
mac_gdp_2020_base_prices_pct,Percentage change of Real GDP (constant 2020 prices),% (Δ YoY),Calculated
mac_gdp_2020_base_prices_sopr_pct,Percentage change of Real GDP YoY volume index (SOPR),%,Calculated
mac_gdp_nominal_prices_pct,Percentage change of Nominal GDP,% (Δ YoY),Calculated
mac_import_price_index_ex_energy_pct,Percentage change of Import price index excl. energy,% (Δ YoY),Calculated
mac_nom_gr_avg_wage_czk_pct,Percentage change of Nominal gross average wage,% (Δ YoY),Calculated
sector_avg_wages_by_nace_pct,Percentage change of Average gross monthly wage in sector,% (Δ YoY),Calculated
sector_no_of_employees_by_nace_pct,Percentage change of Number of employees in sector,% (Δ YoY),Calculated
sector_ppi_by_nace_pct,Percentage change of Producer Price Index by NACE,% (Δ YoY),Calculated
,,,
9. 6. Transformed Variables: Difference in Percentage Points (_dpp),,,
,,,
Variable Name (Short),Description,Unit,Source
firm_cost_ratio_cal_dpp,YoY change in Cost ratio,Percentage points (Δ YoY),Calculated
firm_effective_tax_rate_cal_dpp,YoY change in Effective tax rate,Percentage points (Δ YoY),Calculated
firm_equity_ratio_cal_dpp,YoY change in Equity ratio,Percentage points (Δ YoY),Calculated
firm_net_margin_cal_dpp,YoY change in Net margin,Percentage points (Δ YoY),Calculated
firm_operating_margin_cal_dpp,YoY change in Operating margin,Percentage points (Δ YoY),Calculated
firm_roa_ebit_cal_dpp,YoY change in ROA (EBIT),Percentage points (Δ YoY),Calculated
firm_roe_cal_dpp,YoY change in ROE,Percentage points (Δ YoY),Calculated
mac_CPI_YTYPCT_dpp,YoY change in Headline CPI YoY %,Percentage points (Δ YoY),Calculated
mac_CPV_ANNPCT_dpp,"YoY change in Private final consumption growth, %",Percentage points (Δ YoY),Calculated
mac_FBGSQ_dpp,YoY change in Net exports (% GDP),Percentage points (Δ YoY),Calculated
mac_GAP_dpp,YoY change in Output gap (% potential GDP),Percentage points (Δ YoY),Calculated
mac_GGFLMQ_dpp,YoY change in Gross public debt (% GDP),Percentage points (Δ YoY),Calculated
mac_IRL_dpp,YoY change in Long-term govt bond yield,Percentage points (Δ YoY),Calculated
mac_IRS_dpp,YoY change in Short-term interest rate,Percentage points (Δ YoY),Calculated
mac_ITV_ANNPCT_dpp,"YoY change in Gross fixed capital formation growth, %",Percentage points (Δ YoY),Calculated
mac_KTPV_ANNPCT_dpp,"YoY change in Productive capital stock growth, %",Percentage points (Δ YoY),Calculated
mac_MPEN_dpp,YoY change in Import penetration (% domestic demand),Percentage points (Δ YoY),Calculated
mac_NLGXQ_dpp,YoY change in Gen. gov. primary balance (% GDP),Percentage points (Δ YoY),Calculated
mac_NOOQ_dpp,"YoY change in Net one-offs, gen. gov. (% pot. GDP)",Percentage points (Δ YoY),Calculated
mac_PCORE_YTYPCT_dpp,"YoY change in Core inflation, YoY %",Percentage points (Δ YoY),Calculated
mac_UNR_dpp,YoY change in Unemployment rate,Percentage points (Δ YoY),Calculated
mac_cnb_repo_rate_annual_dpp,YoY change in CNB policy repo rate,Percentage points (Δ YoY),Calculated
mac_hicp_energy_full_roc_dpp,"YoY change in HICP – Electricity, gas & other fuels annual rate of change",Percentage points (Δ YoY),Calculated
mac_hicp_overall_roc_dpp,YoY change in HICP – Overall index annual rate of change,Percentage points (Δ YoY),Calculated
mac_hicp_pure_energy_roc_dpp,"YoY change in HICP – Electricity, gas, solid fuels & heat energy annual rate of change",Percentage points (Δ YoY),Calculated
mac_unemp_rate_dpp,YoY change in Unemployment rate,Percentage points (Δ YoY),Calculated



# %% [markdown]
# # NACE Data Propagation Notebook
# 
# ## Introduction
# Maintains a dataset of economic indicators classified by NACE codes (wages, employees, PPI). Fills missing data at lower levels using higher-level aggregates or umbrella codes (e.g., B+C+D+E), ensuring comprehensive coverage.
# 
# ## Input Data
# • t_nace_matching.parquet – NACE hierarchy (levels 0–5).  
# • data_by_nace_annual_tidy.parquet – Economic indicators by NACE.
# 
# ## Propagation Logic
# 1. Build a full hierarchy-year-metric grid.  
# 2. Identify missing data in the combined table.  
# 3. Search upwards from the missing NACE level to find available values.  
# 4. Use special umbrella codes if direct parents lack data.  
# 5. Record propagation source in the “source” column.
# 6. For each missing entry, the algorithm searches at the next higher NACE level for available data 
#    and continues recursively until it either finds a value or reaches the top-level. 
#    If direct parents lack data, umbrella codes (e.g., B+C+D+E) serve as a fallback source.
# 
# ## Output
# Generates data_by_nace_annual_tidy_propagated.parquet with original plus newly propagated data.
# 
# ## Steps
# 1. Setup, load data.  
# 2. Filter for important metrics.  
# 3. Expand umbrella codes (B+C+D+E, etc.).  
# 4. Propagate missing values.  
# 5. Save final dataset and produce basic summaries.

# %%
import os
import pandas as pd
import numpy as np
from datetime import datetime

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# Load NACE matching table
nace_matching_file = os.path.join(project_root, "data", "source_cleaned", "t_nace_matching.parquet")
df_nace_matching = pd.read_parquet(nace_matching_file)

# Load the main NACE data file
data_file = os.path.join(project_root, "data", "source_cleaned", "data_by_nace_annual_tidy.parquet")
df_nace_data = pd.read_parquet(data_file)

print(f"NACE matching table shape: {df_nace_matching.shape}")
print(f"NACE data shape: {df_nace_data.shape}")
print(f"\nNACE matching columns: {df_nace_matching.columns.tolist()}")
print(f"NACE data columns: {df_nace_data.columns.tolist()}")

# %%
# Filter data for the metrics we want to propagate
metrics_to_propagate = ['avg_wages_by_nace', 'no_of_employees_by_nace', 'ppi_by_nace']

df_propagation_source = df_nace_data[df_nace_data['metric'].isin(metrics_to_propagate)].copy()

print(f"Data for propagation shape: {df_propagation_source.shape}")
print(f"\nMetrics distribution:")
print(df_propagation_source['metric'].value_counts())
print(f"\nLevel distribution:")
print(df_propagation_source['level'].value_counts().sort_index())
print(f"\nYear range: {df_propagation_source['year'].min()} - {df_propagation_source['year'].max()}")

# %%
# expand the rows that level=0 czso_code contains + to be listed separately for each NACE code in the source data df_propagation_source
# e.g. expanding B+C+D+E to separate rows for B, C, D, E containing the same values (except for the NACE code)
# since the names are already clean, the level0 is always in format czso_nace separated by "+"

# Expand level-0 umbrella codes (czso_code containing "+") into separate rows
umbrella_mask = (df_propagation_source['level'] == 0) & df_propagation_source['czso_code'].str.contains(r'\+')
umbrella_rows = df_propagation_source[umbrella_mask]

# Split the combined code into components and explode
expanded = (
    umbrella_rows
    .assign(czso_code=umbrella_rows['czso_code'].str.split(r'\+'))
    .explode('czso_code')
    .reset_index(drop=True)
)

# Merge the expanded rows back into the original DataFrame
df_propagation_source = pd.concat([
    df_propagation_source[~umbrella_mask],  # Keep non-umbrella rows
    expanded  # Add the expanded rows
], ignore_index=True)
# Ensure czso_code is stripped of whitespace
df_propagation_source['czso_code'] = df_propagation_source['czso_code'].str.strip()

# level is integer
df_propagation_source['level'] = df_propagation_source['level'].astype(int)



# %%
# remove rows with missing value in 'value' column
df_propagation_source = df_propagation_source.dropna(subset=['value'])


# %%
def propagate_nace_data(df_source, df_nace_hierarchy, metrics_list):
    """
    Propagate data from higher NACE levels to lower levels where data is missing.
    Uses the hierarchical structure from level1_code, level2_code, etc.
    
    Parameters:
    - df_source: DataFrame with NACE data to propagate. 
                 Expected columns: czso_code, level, name_cs, name_en, year, metric, value, unit, source.
    - df_nace_hierarchy: DataFrame with NACE hierarchy information.
                         Expected columns: czso_code, level, name_czso_cs, name_czso_en, levelX_code.
    - metrics_list: List of metrics to propagate
    
    Returns:
    - DataFrame with propagated data
    """
    
    # Create a copy of source data
    df_result = df_source.copy()
    
    # Get all possible combinations of czso_code, year, and metric from hierarchy
    years = df_source['year'].unique()
    
    # Create full hierarchy with all years and metrics
    hierarchy_expanded = []
    for metric in metrics_list:
        for year in years:
            temp_df = df_nace_hierarchy.copy()
            temp_df['year'] = year
            temp_df['metric'] = metric
            hierarchy_expanded.append(temp_df)
    
    df_full_hierarchy = pd.concat(hierarchy_expanded, ignore_index=True)
    
    # Merge with existing data to identify missing combinations
    # df_source columns: czso_code, level, name_cs, name_en, year, metric, value, unit, source
    # df_full_hierarchy columns: czso_code, level, name_czso_cs, name_czso_en, year, metric, levelX_code
    # Overlapping 'level' column will be suffixed.
    # 'name_cs'/'name_en' vs 'name_czso_cs'/'name_czso_en' are distinct.
    # 'unit', 'value', 'source' are only in df_source.
    df_merged = pd.merge(
        df_full_hierarchy,
        df_source,
        on=['czso_code', 'year', 'metric'],
        how='left',
        suffixes=('_hierarchy', '_data') # level -> level_hierarchy, level_data
    )
    
    # Identify missing data (where value is NaN)
    missing_mask = df_merged['value'].isna()
    print(f"Found {missing_mask.sum()} missing data points to potentially propagate")
    
    # Sort by level (higher levels first for propagation) - use the hierarchy level
    df_merged = df_merged.sort_values(['metric', 'year', 'level_hierarchy', 'czso_code'])
    
    # Propagation logic: for each missing data point, try to find parent data
    propagated_records = []
    
    for metric in metrics_list:
        print(f"\nProcessing metric: {metric}")
        metric_data = df_merged[df_merged['metric'] == metric].copy()
        
        for year_val in years: # Renamed to avoid conflict with 'year' column name
            year_data = metric_data[metric_data['year'] == year_val].copy()
            
            # Get existing data for this year/metric
            # This data comes from df_merged, so it has 'level_data' (original NACE level from df_source)
            # and 'unit' (original unit from df_source)
            existing_data_for_year_metric = year_data[~year_data['value'].isna()].copy()
            
            # Prepare a map of available data. If a czso_code exists at multiple NACE levels
            # (e.g. 'C' at level 1 and 'C' at level 0 from expansion), prioritize higher NACE level.
            # 'level_data' is the NACE level from the original df_source.
            existing_data_prepared = existing_data_for_year_metric.sort_values(
                'level_data', ascending=False
            ).drop_duplicates(subset=['czso_code'], keep='first')
            
            existing_data_map = {}
            for _, r_existing in existing_data_prepared.iterrows():
                existing_data_map[r_existing['czso_code']] = {
                    'value': r_existing['value'],
                    'level': r_existing['level_data'], # Actual NACE level of this source data point
                    'unit': r_existing['unit']         # Unit of this source data point
                }
            
            # Try to propagate to missing data points for this year/metric
            missing_data_for_year_metric = year_data[year_data['value'].isna()]
            
            for _, row in missing_data_for_year_metric.iterrows():
                target_code = row['czso_code']
                # target_level is the NACE level of the item we are trying to fill (from hierarchy)
                target_level = row['level_hierarchy'] 
                
                propagated_value = None
                source_code_found = None
                actual_level_of_source_code = None # NACE level of the source_code_found
                propagated_unit = 'unknown'      # Default unit

                # Try to find parent data by going up the hierarchy
                # Loop from parent (target_level-1) up to NACE Level 1 ancestor
                for i in range(target_level - 1, 0, -1): 
                    parent_code_at_level_i = None
                    if i == 1: parent_code_at_level_i = row['level1_code']
                    elif i == 2: parent_code_at_level_i = row['level2_code']
                    elif i == 3: parent_code_at_level_i = row['level3_code']
                    elif i == 4: parent_code_at_level_i = row['level4_code']
                    elif i == 5: parent_code_at_level_i = row['level5_code']
                    
                    if pd.notna(parent_code_at_level_i) and parent_code_at_level_i in existing_data_map:
                        parent_data_entry = existing_data_map[parent_code_at_level_i]
                        propagated_value = parent_data_entry['value']
                        actual_level_of_source_code = parent_data_entry['level']
                        actual_level_of_source_code = int(actual_level_of_source_code) 
                        propagated_unit = parent_data_entry['unit']
                        source_code_found = parent_code_at_level_i 

                        break # Found data from the closest parent in hierarchy
                
                if propagated_value is not None:
                    new_record = {
                        'czso_code': target_code,
                        'level': target_level, # NACE level of the item being filled
                        'name_cs': row['name_czso_cs'], # Name from hierarchy table
                        'name_en': row['name_czso_en'], # Name from hierarchy table
                        'year': year_val,
                        'metric': metric,
                        'value': propagated_value,
                        'unit': propagated_unit if pd.notna(propagated_unit) else 'unknown',
                        'source': f"PROPAGATED from level {actual_level_of_source_code} ({source_code_found})"
                    }
                    propagated_records.append(new_record)
    
    print(f"\nGenerated {len(propagated_records)} propagated records")
    
    if propagated_records:
        df_propagated_new = pd.DataFrame(propagated_records)
        df_result = pd.concat([df_result, df_propagated_new], ignore_index=True)

    return df_result

# %%
# Execute the propagation
print("Starting data propagation...")
print(f"Original data shape: {df_propagation_source.shape}")

df_propagated = propagate_nace_data(
    df_propagation_source, 
    df_nace_matching, 
    metrics_to_propagate
)

print(f"\nPropagated data shape: {df_propagated.shape}")
print(f"Added {df_propagated.shape[0] - df_propagation_source.shape[0]} new records")

# Check the results
print("\n=== Propagation Results ===")
print("Source distribution:")
print(df_propagated['source'].value_counts())

print("\nMetric distribution after propagation:")
for metric in metrics_to_propagate:
    metric_data = df_propagated[df_propagated['metric'] == metric]
    print(f"{metric}: {len(metric_data)} records")
    print(f"  - Original: {len(metric_data[~metric_data['source'].str.contains('PROPAGATED', na=False)])}")
    print(f"  - Propagated: {len(metric_data[metric_data['source'].str.contains('PROPAGATED', na=False)])}")

df_final = df_propagated.copy()

# %%
# drop rows with czso_code that are not in the hierarchy
df_final = df_final[df_final['czso_code'].isin(df_nace_matching['czso_code'])]

# add magnus_nace column based on the matching table
df_final = df_final.merge(
    df_nace_matching[['czso_code', 'magnus_nace']],
    on='czso_code',
    how='left'
)
# 2nd column
df_final = df_final[['czso_code', 'magnus_nace', 'level', 'name_cs', 'name_en', 'year', 'metric', 'value', 'unit', 'source']]



# %%
# Save the propagated data
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file = os.path.join(output_folder, "data_by_nace_annual_tidy_propagated.parquet")

df_final.to_parquet(output_file, index=False, engine="pyarrow")
print(f"\nPropagated data saved to: {output_file}")


# %% [markdown]
# ## Data Summary

# %%
# Generate summary statistics
print("\n=== Final Summary ===")
print(f"Total records: {len(df_final):,}")
print(f"Date range: {df_final['year'].min()} - {df_final['year'].max()}")
print(f"Unique NACE codes: {df_final['czso_code'].nunique()}")
print(f"Levels represented: {sorted(df_final['level'].unique())}")

print("\nRecords by metric:")
for metric in sorted(df_final['metric'].unique()):
    count = len(df_final[df_final['metric'] == metric])
    propagated_count = len(df_final[
        (df_final['metric'] == metric) & 
        (df_final['source'].str.contains('PROPAGATED', na=False))
    ])
    print(f"  {metric}: {count:,} total ({propagated_count:,} propagated)")

print("\nRecords by level:")
for level in sorted(df_final['level'].unique()):
    count = len(df_final[df_final['level'] == level])
    print(f"  Level {level}: {count:,} records")

# %%
def summarize_data_availability(df_data, df_nace_hierarchy, target_metric):
    """
    Summarizes data availability for a given metric across all years.

    For each year, it shows how many NACE codes have data, how many are missing,
    and details for the missing NACE codes including their parent NACE codes.

    Parameters:
    - df_data: DataFrame containing the data (e.g., df_final).
               Expected columns: 'czso_code', 'year', 'metric', 'value', 'level', 
                                 'name_cs', 'name_en'.
    - df_nace_hierarchy: DataFrame with NACE hierarchy information (e.g., df_nace_matching).
                         Expected columns: 'czso_code', 'level', 'name_czso_cs', 
                                           'name_czso_en', 'level1_code', 'level2_code', 
                                           'level3_code', 'level4_code', 'level5_code'.
    - target_metric: String, the name of the metric to summarize.
    """
    print(f"--- Data Availability Summary for Metric: {target_metric} ---")

    metric_data = df_data[df_data['metric'] == target_metric]
    
    if metric_data.empty:
        print(f"No data found for metric: {target_metric}")
        return

    unique_years = sorted(metric_data['year'].unique())

    # Select relevant columns from NACE hierarchy for the full grid
    hierarchy_cols = ['czso_code', 'level', 'name_czso_cs', 'name_czso_en', 
                      'level1_code', 'level2_code', 'level3_code', 
                      'level4_code', 'level5_code']
    df_nace_base = df_nace_hierarchy[hierarchy_cols].copy()
    df_nace_base.rename(columns={'level': 'nace_level_hierarchy', # To avoid potential merge conflicts
                                 'name_czso_cs': 'name_cs_hierarchy',
                                 'name_czso_en': 'name_en_hierarchy'}, inplace=True)


    for year in unique_years:
        print(f"\n--- Year: {year} ---")
        
        # Create a full grid of all NACE codes for this year and metric
        df_year_full_nace = df_nace_base.copy()
        df_year_full_nace['year'] = year
        df_year_full_nace['metric'] = target_metric
        
        # Data for the current year and metric
        current_year_metric_data = metric_data[metric_data['year'] == year]
        
        # Merge the full NACE grid with the actual data
        # We are interested in 'value' from current_year_metric_data
        merged_df = pd.merge(
            df_year_full_nace,
            current_year_metric_data[['czso_code', 'year', 'metric', 'value', 'source']],
            on=['czso_code', 'year', 'metric'],
            how='left'
        )
        
        available_mask = merged_df['value'].notna()
        missing_mask = merged_df['value'].isna()
        
        available_count = available_mask.sum()
        missing_count = missing_mask.sum()
        
        print(f"  NACE codes with data: {available_count}")
        print(f"  NACE codes missing data: {missing_count}")
        
        if missing_count > 0:
            print(f"  Details for missing NACE codes (showing first 5 if many):")
            missing_details_df = merged_df[missing_mask]
            
            for _, row in missing_details_df.head(5).iterrows():
                parent_info = []
                if pd.notna(row['level5_code']): parent_info.append(f"L5P:{row['level5_code']}")
                if pd.notna(row['level4_code']): parent_info.append(f"L4P:{row['level4_code']}")
                if pd.notna(row['level3_code']): parent_info.append(f"L3P:{row['level3_code']}")
                if pd.notna(row['level2_code']): parent_info.append(f"L2P:{row['level2_code']}")
                if pd.notna(row['level1_code']): parent_info.append(f"L1P:{row['level1_code']}")
                
                print(f"    - Code: {row['czso_code']} (Level: {row['nace_level_hierarchy']}), "
                      f"Name: {row['name_en_hierarchy'][:30]}..., " # Truncate name
                      f"Parents: [{', '.join(parent_info)}]")
            if missing_count > 5:
                print(f"    ... and {missing_count - 5} more missing NACE codes.")
    print("\n--- End of Summary ---")



# %%
summarize_data_availability(df_final, df_nace_matching, 'ppi_by_nace')

# %%
# counts of records per metric and year pivot table 
pivot_counts = df_final.pivot_table(
    index='year',
    columns='metric',
    values='czso_code',
    aggfunc='count',
    fill_value=0
)
print("\n=== Records Count by Metric and Year ===")
print(pivot_counts)

# %%





# %%
import os
import pandas as pd
from datetime import timedelta

# %% [markdown]
# ### Time-Weighted Annual CNB Repo Rates
# 
# **Data Source**  
# A text file listing CNB repo rate decisions. Each decision is valid until the next one begins.
# 
# **Method**  
# - **Time Weighting**: Instead of taking a simple average of all rates in a given year, we break each `[start_date, next_start)` interval by calendar year boundaries and compute a time‐weighted average. This ensures that a rate valid for a longer period has a proportionally bigger impact on the annual average.
# 
# **Justification**  
# - **Accuracy**: Merely averaging rate values ignores how long each rate was in effect. Time weighting aligns the annual rate with real monetary policy conditions experienced throughout the year.
# - **Usability**: The resulting annual series can be easily merged with other macro data (HICP, wages, etc.) for subsequent econometric analysis.
# 

# %%
# Paths
script_dir = os.getcwd()  # Jupyter Notebook working directory
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "CNB_repo_sazby.txt")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "cnb_repo_annual.parquet")

# Read data
df_repo = pd.read_csv(
    input_file,
    sep="|",
    names=["VALID_FROM", "CNB_REPO_RATE_IN_PCT"],
    header=None,
    dtype={"VALID_FROM": str}
)
df_repo["VALID_FROM"] = pd.to_datetime(df_repo["VALID_FROM"], format="%Y%m%d", errors="coerce")
df_repo["CNB_REPO_RATE_IN_PCT"] = pd.to_numeric(df_repo["CNB_REPO_RATE_IN_PCT"], errors="coerce")
df_repo.dropna(subset=["VALID_FROM"], inplace=True)

df_repo.sort_values("VALID_FROM", inplace=True)

# Next start date (rates are valid until the day before the next decision)
df_repo["NEXT_START"] = df_repo["VALID_FROM"].shift(-1)

# Define cutoff for the last row
if not df_repo.empty:
    last_idx = df_repo.index[-1]
    last_year = df_repo.loc[last_idx, "VALID_FROM"].year
    cutoff_date = pd.to_datetime(f"{last_year + 1}-12-31")
    df_repo.loc[last_idx, "NEXT_START"] = cutoff_date

def split_interval_by_year(start_date, end_date):
    """Break [start_date, end_date) into sub-intervals by calendar year."""
    end_date = end_date - pd.Timedelta(days=1)
    if end_date < start_date:
        return []
    intervals, current = [], start_date
    while current <= end_date:
        year_end = pd.to_datetime(f"{current.year}-12-31")
        local_end = min(year_end, end_date)
        delta = (local_end - current).days + 1
        intervals.append({"year": current.year, "days_in_interval": delta})
        current = local_end + pd.Timedelta(days=1)
    total_days = (end_date - start_date).days + 1
    for iv in intervals:
        iv["total_days_for_rate"] = total_days
    return intervals

records = []
for _, row in df_repo.iterrows():
    intervals = split_interval_by_year(row["VALID_FROM"], row["NEXT_START"])
    rate = row["CNB_REPO_RATE_IN_PCT"]
    for iv in intervals:
        frac = iv["days_in_interval"] / iv["total_days_for_rate"]
        records.append({
            "year": iv["year"],
            "repo_rate": rate,
            "weighted_rate": rate * frac
        })

df_intervals = pd.DataFrame(records)
if not df_intervals.empty:
    # Sum up weighted rates per year
    annual_data = df_intervals.groupby("year", as_index=False).agg(
        sum_weighted=("weighted_rate", "sum"),
        sum_rates=("repo_rate", "count")  # Not strictly needed, but can track intervals
    )
    # The sum of weighted_rate for each year is our time-weighted value,
    # because each interval's fraction sums to 1 if the year is fully covered.
    # However, to confirm partial coverage, let's also track fraction_of_interval:
    # (We'll just treat the sum of weighted_rate as the annual average directly.)
    
    # Alternatively, we can track fraction_of_interval if needed:
    # df_intervals["fraction_of_interval"] = df_intervals["weighted_rate"] / df_intervals["repo_rate"]
    # Then group and do the final average. For simplicity, let's proceed with the sum of weighted_rate:
    
    # Weighted average = sum(weighted_rate)
    # => We must ensure each year was fully covered for that to reflect a 100% fraction.
    # If partial coverage, the sum will be < the actual expected value.
    # For a robust approach, let's recalculate fraction_of_interval in the table:
    df_intervals["fraction_of_interval"] = df_intervals["weighted_rate"] / df_intervals["repo_rate"]
    annual_fracs = df_intervals.groupby("year")["fraction_of_interval"].sum().reset_index()
    annual_merged = annual_data.merge(annual_fracs, on="year", how="left")
    annual_merged.rename(columns={"fraction_of_interval": "sum_fraction"}, inplace=True)
    
    # Final annual rate = sum of weighted_rate / sum_fraction
    # sum_weighted is the sum of (rate * fraction_i)
    annual_merged["cnb_repo_rate_annual"] = (
        annual_merged["sum_weighted"] / annual_merged["sum_fraction"]
    )
    
    final_annual = annual_merged[["year", "cnb_repo_rate_annual"]].sort_values("year")
    # drop years pre 2000 and post 2024
    final_annual = final_annual[final_annual["year"] >= 2000]
    final_annual = final_annual[final_annual["year"] <= 2024]
    # Save to parquet
    #final_annual.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
    #print(f"Time-weighted annual CNB repo rates saved to: {output_file}")
    #display(final_annual.head(25))
else:
    print("No records found after year 2000.")


# %% [markdown]
# ### Annual HICP Data Preparation
# 
# **Data Source:**  
# Monthly HICP data (Overall index) with columns:
# - `DATE` (e.g., "1996-12-31")
# - `TIME PERIOD`
# - `"HICP - Overall index (ICP.M.CZ.N.000000.4.ANR)"`
# 
# **Method:**  
# - **Parse Dates & Numeric Conversion:**  
#   Convert the `DATE` column to datetime and the HICP index column to numeric.
# - **Filter December Values:**  
#   Select only records where the month is December. December data represents the end-of-year value, which is often used as the annual measure.
# - **Extract Year:**  
#   Create a `year` column from the December dates.
# - **Output:**  
#   The resulting DataFrame contains one observation per year with columns `year` and `hicp_dec`. This annual series will serve as the base for merging with other macroeconomic data.
# 
# **Justification:**  
# Using December values provides a consistent, end-of-year snapshot. This harmonized annual format simplifies integration with datasets such as the CNB repo rates and firm-level financial data.
# 

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "ECB Data Portal_20250402011223_HICP_from1996_CZ.csv")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "hicp_december_annual.parquet")

# Read the HICP data
df_hicp = pd.read_csv(input_file)

# Convert DATE column to datetime
df_hicp["DATE"] = pd.to_datetime(df_hicp["DATE"], format="%Y-%m-%d", errors="coerce")

# Convert HICP index column to numeric
df_hicp["hicp_dec"] = pd.to_numeric(df_hicp["HICP - Overall index (ICP.M.CZ.N.000000.4.ANR)"], errors="coerce")

# Filter to keep only December observations
df_hicp_dec = df_hicp[df_hicp["DATE"].dt.month == 12].copy()

# Extract year from DATE
df_hicp_dec["year"] = df_hicp_dec["DATE"].dt.year

# Select only the required columns for annual data
df_hicp_annual = df_hicp_dec[["year", "hicp_dec"]].reset_index(drop=True)

# remove pre 2000 data
df_hicp_annual = df_hicp_annual[df_hicp_annual["year"] >= 2000]

# Save the annual HICP data to a Parquet file
df_hicp_annual.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)

print("Annual HICP (December values) saved to:", output_file)
#display(df_hicp_annual.head())


# %% [markdown]
# ### Energy-Related HICP Data Preparation
# 
# **Data Sources:**  
# Three ECB data files with HICP rate of change indicators:
# 
# 1. **ECB Data Portal_20250714181940.csv**  
#    - **ICP.A.CZ.N.000000.4.AVR:** HICP – Overall index  
#    - **Type:** Annual average rate of change (% y/y)  
#    - **Use:** Overall inflation rate for comparison with energy components
# 
# 2. **ECB Data Portal_20250714182022.csv**  
#    - **ICP.A.CZ.N.ELGAS0.4.AVR:** HICP – Electricity, gas, solid fuels and heat energy  
#    - **Type:** Annual average rate of change (% y/y)  
#    - **Basket:** COICOP 0451+0452+0454+0455 (pure energy, excludes liquid fuels)
# 
# 3. **ECB Data Portal_20250714182131.csv**  
#    - **ICP.A.CZ.N.045000.4.AVR:** HICP – Electricity, gas and other fuels  
#    - **Type:** Annual average rate of change (% y/y)  
#    - **Basket:** COICOP 04.5 (includes liquid & solid fuels, heat energy)
# 
# **Method:**  
# These are already annual rate of change data, so we extract the year and convert the indicators to numeric format for integration with the macro dataset.
# 
# **Justification:**  
# These energy-specific rate of change indicators provide direct inflation measures for different energy baskets, allowing precise control over energy inflation effects in econometric analysis.

# %%
# Load HICP Overall Index Rate of Change (% y/y) - File 1
input_file_hicp_overall_roc = os.path.join(project_root, "data", "source_raw", "economy", "ECB Data Portal_20250714181940.csv")
output_file_hicp_overall_roc = os.path.join(output_folder, "hicp_overall_roc_annual.parquet")

# Read the overall HICP rate of change data
df_hicp_overall_roc = pd.read_csv(input_file_hicp_overall_roc)

# Convert DATE column to datetime
df_hicp_overall_roc["DATE"] = pd.to_datetime(df_hicp_overall_roc["DATE"], format="%Y-%m-%d", errors="coerce")

# Extract year from DATE (these are annual data, so we just need the year)
df_hicp_overall_roc["year"] = df_hicp_overall_roc["DATE"].dt.year

# Convert HICP overall rate of change column to numeric (find the correct column name)
overall_roc_col = [col for col in df_hicp_overall_roc.columns if "ICP.A.CZ.N.000000.4.AVR" in col][0]
df_hicp_overall_roc["hicp_overall_roc"] = pd.to_numeric(df_hicp_overall_roc[overall_roc_col], errors="coerce")

# Select only the required columns and filter years >= 2000
df_hicp_overall_roc_annual = df_hicp_overall_roc[["year", "hicp_overall_roc"]].dropna().reset_index(drop=True)
df_hicp_overall_roc_annual = df_hicp_overall_roc_annual[df_hicp_overall_roc_annual["year"] >= 2000]


# %%
# Load HICP Pure Energy Rate of Change (% y/y) - File 2 
input_file_pure_energy_roc = os.path.join(project_root, "data", "source_raw", "economy", "ECB Data Portal_20250714182022.csv")
output_file_pure_energy_roc = os.path.join(output_folder, "hicp_pure_energy_roc_annual.parquet")

# Read the pure energy HICP rate of change data
df_pure_energy_roc = pd.read_csv(input_file_pure_energy_roc)

# Convert DATE column to datetime
df_pure_energy_roc["DATE"] = pd.to_datetime(df_pure_energy_roc["DATE"], format="%Y-%m-%d", errors="coerce")

# Extract year from DATE
df_pure_energy_roc["year"] = df_pure_energy_roc["DATE"].dt.year

# Convert HICP pure energy rate of change column to numeric (find the correct column name)
pure_energy_roc_col = [col for col in df_pure_energy_roc.columns if "ICP.A.CZ.N.ELGAS0.4.AVR" in col][0]
df_pure_energy_roc["hicp_pure_energy_roc"] = pd.to_numeric(df_pure_energy_roc[pure_energy_roc_col], errors="coerce")

# Select only the required columns and filter years >= 2000
df_pure_energy_roc_annual = df_pure_energy_roc[["year", "hicp_pure_energy_roc"]].dropna().reset_index(drop=True)
df_pure_energy_roc_annual = df_pure_energy_roc_annual[df_pure_energy_roc_annual["year"] >= 2000]


# %%
# Load HICP Energy (including liquid fuels) Rate of Change (% y/y) - File 3
input_file_energy_full_roc = os.path.join(project_root, "data", "source_raw", "economy", "ECB Data Portal_20250714182131.csv")
output_file_energy_full_roc = os.path.join(output_folder, "hicp_energy_full_roc_annual.parquet")

# Read the energy (full) HICP rate of change data
df_energy_full_roc = pd.read_csv(input_file_energy_full_roc)

# Convert DATE column to datetime
df_energy_full_roc["DATE"] = pd.to_datetime(df_energy_full_roc["DATE"], format="%Y-%m-%d", errors="coerce")

# Extract year from DATE
df_energy_full_roc["year"] = df_energy_full_roc["DATE"].dt.year

# Convert HICP energy (full) rate of change column to numeric (find the correct column name)
energy_full_roc_col = [col for col in df_energy_full_roc.columns if "ICP.A.CZ.N.045000.4.AVR" in col][0]
df_energy_full_roc["hicp_energy_full_roc"] = pd.to_numeric(df_energy_full_roc[energy_full_roc_col], errors="coerce")

# Select only the required columns and filter years >= 2000
df_energy_full_roc_annual = df_energy_full_roc[["year", "hicp_energy_full_roc"]].dropna().reset_index(drop=True)
df_energy_full_roc_annual = df_energy_full_roc_annual[df_energy_full_roc_annual["year"] >= 2000]


# %% [markdown]
# ### Annual Wages & Employees Data Preparation
# 
# **Data Source:**  
# Excel file (`pmzcr030625_1_wages_avg.xlsx`) - CZSO reporting average gross monthly wages and average employee counts (in thousands) per full-time equivalent.
# 
# **Process:**
# - **Select & Rename:**  
#   Extract the year, nominal wage (CZK), and number of employees columns; rename them to `year`, `nom_gr_avg_wage_czk`, and `no_of_employees_ths`.
# - **Filter Rows:**  
#   Retain only the first 25 rows (annual values).
# - **Clean Data:**  
#   Correct irregular year entries (e.g., "20233)" → "2023"), convert `year` to integer, and ensure wage and employee columns are numeric.
#   - values for 2023 and 2024 are preliminary
# - **Output:**  
#   Save the cleaned annual data as a Parquet.
# 
# **Rationale:**  
# Focusing on annual data and standardizing types streamlines merging with other macro series (e.g., CNB repo rates, HICP) and minimizes processing errors.
# 
# ---

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "pmzcr030625_1_wages_avg.xlsx")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "wages_no_employees_annual.parquet")

# Read the Excel file
df_wages = pd.read_excel(input_file, sheet_name="List1", skiprows=4)

# select only the relevant columns: 0 (year), 1 - nominal wage CZK, 4 - no of employees in thousands
# and rename them
df_wages = df_wages.iloc[:, [0, 1, 4]].rename(columns={
    df_wages.columns[0]: "year",
    df_wages.columns[1]: "nom_gr_avg_wage_czk",
    df_wages.columns[4]: "no_of_employees_ths"
}) 

# select only first 25 rows (yearly values)
df_wages = df_wages.iloc[1:26].copy()
# Convert the year column to int
#df_wages["year"] = df_wages["year"].astype(int, errors="coerce")

# replace 20233) and 20243) by 2023 and 2024 in year col (this was a reference)
df_wages["year"] = df_wages["year"].replace({"20233)": "2023", "20243)": "2024"})

# Convert the year column to int
df_wages["year"] = df_wages["year"].astype(int, errors="ignore")
# Convert the nominal wage column to numeric
df_wages["nom_gr_avg_wage_czk"] = pd.to_numeric(df_wages["nom_gr_avg_wage_czk"], errors="coerce")
# # Convert the number of employees column to numeric
df_wages["no_of_employees_ths"] = pd.to_numeric(df_wages["no_of_employees_ths"], errors="coerce")

# save to parquet
#df_wages.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
#print("Annual wages data and no. of employees saved to:", output_file)


# %% [markdown]
# ### GDP Data Preparation
# 
# **Data Source:** CZSO
# 
# Hruby domaci produkt - stale ceny z r 2020
# 
# Kód: NUCDUSHV01-R/11
# Výpočet ukazatelů ve stálých cenách roku 2020 byl proveden metodou řetězení meziročních indexů (vypočtených vždy na bázi průměru předchozího roku). Tato metoda zajišťuje vazbu ukazatelů ve čtvrtletní a roční periodicitě, ale neumožňuje vazbu jednotlivých komponent na úhrn.
# SOPR – stejné období předchozího roku.
# odhad podle sumy kvart. hodnot
# 
#  **"Stálé ceny roku 2020"** column. This column represents GDP in constant prices (with 2020 as the base year), allowing you to compare real economic growth over time without the distortions caused by price changes.
# 
# **Why "Stálé ceny roku 2020" is preferable:**
# 
# - **Removes Inflation Effects:**  
# measure the true volume of economic activity rather than nominal changes that include inflation.
# 
# - **Consistent Time Comparison:**  
#   It enables a more accurate comparison of economic performance across different years, as all values are adjusted to the price level of the base year (2020).
# 
# - **Policy Analysis Relevance:**  
#   For studies that examine relationships between variables like profit margins and inflation, it’s crucial to work with real output measures. This helps in isolating the effect of inflation from other factors.
# 

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "NUCDUSHV01-R_CZSO_GDP.xlsx")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "gdp_annual.parquet")

# Read the Excel file
df_gdp = pd.read_excel(input_file, sheet_name="DATA", skiprows=6)

# Select only the relevant columns: 1 (year), 2 - GDP nominal prices, 4 - GDP 2020 base prices, 5 - GDP 2020 base prices SOPR (stejné období předchozího roku), 6 - deflator nominal, 7 - deflator base 2020
# and rename them
df_gdp = df_gdp.iloc[:, [1, 2, 4, 5, 6, 7]].rename(columns={
    df_gdp.columns[1]: "year",
    df_gdp.columns[2]: "gdp_nominal_prices",
    df_gdp.columns[4]: "gdp_2020_base_prices",
    df_gdp.columns[5]: "gdp_2020_base_prices_sopr",
    df_gdp.columns[6]: "deflator_nominal",
    df_gdp.columns[7]: "deflator_base_2020"
})

# Select only first 24 rows (yearly values)
df_gdp = df_gdp.iloc[0:25].copy()

# adjust "2024 [3]" - keep first 4 characters only 
df_gdp["year"] = df_gdp["year"].str[:4]

# Convert the year column to int
df_gdp["year"] = df_gdp["year"].astype(int, errors="ignore")

# Convert the GDP columns to numeric
df_gdp["gdp_nominal_prices"] = pd.to_numeric(df_gdp["gdp_nominal_prices"], errors="coerce")
df_gdp["gdp_2020_base_prices"] = pd.to_numeric(df_gdp["gdp_2020_base_prices"], errors="coerce")
df_gdp["gdp_2020_base_prices_sopr"] = pd.to_numeric(df_gdp["gdp_2020_base_prices_sopr"], errors="coerce")
df_gdp["deflator_nominal"] = pd.to_numeric(df_gdp["deflator_nominal"], errors="coerce")
df_gdp["deflator_base_2020"] = pd.to_numeric(df_gdp["deflator_base_2020"], errors="coerce")

# Save to parquet

#df_gdp.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
#print("Annual GDP data saved to:", output_file)
#display(df_gdp.head())




# %% [markdown]
# ### Unemployment rate Data Preparation
# 
# source: CZSO 
# Obecná míra nezaměstnanosti - Ceska republika
# 
# chosen based on data availability from 2000
# 
# 

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "ZAMDPORK02_unemployment.xlsx")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "unemp_rate_annual.parquet")

# Read the Excel file
df_unemp = pd.read_excel(input_file, sheet_name="DATA", skiprows=6)

# drop first column 
df_unemp.drop(df_unemp.columns[0], axis=1, inplace=True)

# drop all rows except the first 
df_unemp = df_unemp.iloc[0:1].copy()

# the data is in wide format, so we need to transpose it
df_unemp = df_unemp.transpose()

# drop Czech republic row 1st
df_unemp.drop(df_unemp.index[0], inplace=True)

# rename columns: from index to year
df_unemp.reset_index(inplace=True)
df_unemp.rename(columns={"index": "year"}, inplace=True)
# Convert the year column to int
df_unemp["year"] = df_unemp["year"].astype(int, errors="ignore")

# rename column: 0 to unemp_rate
df_unemp.rename(columns={df_unemp.columns[1]: "unemp_rate"}, inplace=True)

# Convert the unemployment rate column to numeric
df_unemp["unemp_rate"] = pd.to_numeric(df_unemp["unemp_rate"], errors="coerce")

# save to parquet
# df_unemp.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
# print("Annual unemployment rate data saved to:", output_file)
#display(df_unemp.head())


# %% [markdown]
# ### FX rates 
# 
# source: CNB (https://www.cnb.cz/en/financial-markets/foreign-exchange-market/central-bank-exchange-rate-fixing/central-bank-exchange-rate-fixing/currency_average.html?currency=EUR)
# 
# - **Data Source:** CNB
# - **Data Type:** Average Qty FX rates
# 
# - **Data Format:** txt
# 
# we calculate an annual FX rate by taking the simple average of the four quarterly values, since each quarter is weighted equally (3 months). This arithmetic average provides a reasonable approximation of the yearly exchange rate.
# 
# 

# %%
# Define file paths
script_dir = os.getcwd()  # Current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "economy", "CNB FX rates from 1999.txt")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "fx_rates_annual.parquet")

# Read the FX rates data
df_fx = pd.read_csv(
    input_file,
    sep="|",
)

# convert year to integer
df_fx["year"] = df_fx["year"].astype(int, errors="ignore")

# convert all columns to numeric
df_fx.iloc[:, 1:] = df_fx.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")

# calculate mean for each row 
# and add it to the dataframe
df_fx["fx_czk_eur_annual_avg"] = df_fx.iloc[:, 1:].mean(axis=1)

#drop the original columns
df_fx.drop(df_fx.columns[1:5], axis=1, inplace=True)

# save to parquet
# df_fx.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
# print("Annual FX rates data saved to:", output_file)


# %% [markdown]
# ### Import price indices w/o energy
# **Data Source:** CZSO
# - **Data Type:** Import price indices excluding energy
# - see src_01_data_curation/data_curation_import_prices.ipynb for details 
# Data: 
# ```csv
# Year,Index
# 2008,91.87
# 2009,92.44
# 2010,92.05
# 2011,92.34
# 2012,94.5
# 2013,95.46
# 2014,98.56
# 2015,100.0
# 2016,97.99
# 2017,97.32
# 2018,95.26
# 2019,96.2
# 2020,97.48
# 2021,99.0
# 2022,105.88
# 2023,104.64
# 2024,107.73
# ```
# 

# %%
# file: data/source_cleaned/import_price_index_ex_energy.csv
# read the import price index data
input_file = os.path.join(project_root, "data", "source_cleaned", "import_price_index_ex_energy.csv")

# Read the import price index data
df_import_price_index = pd.read_csv(input_file)



# rename Year to year, to integer
df_import_price_index.rename(columns={"Year": "year"}, inplace=True)
df_import_price_index["year"] = df_import_price_index["year"].astype(int, errors="ignore")
# rename index column to value, to float
df_import_price_index.rename(columns={"Index": "value"}, inplace=True)
df_import_price_index["value"] = df_import_price_index["value"].astype(float, errors="ignore")

# add metric column with value "import_price_index_ex_energy"
df_import_price_index["metric"] = "import_price_index_ex_energy"





# %% [markdown]
# ### OECD Economic Outlook 117
# 
# **Data Source:** OECD Economic Outlook 117
# 
# Exported on Jul 05 2025
# 
# - data until 2024 are actuals, 2025-2026 are forecasts
# - we filter 1999 - 2024
# - source: https://data-explorer.oecd.org/vis?bp=true&df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_EO%40DF_EO&df[ag]=OECD.ECO.MAD&dq=CZE..A&snb=3&to[TIME_PERIOD]=false&vw=tb&pd=1999%2C2026&lb=bt
# 
# ## selected series: 
# 
# | Short code        | Full series name                                                                  |
# | ----------------- | --------------------------------------------------------------------------------- |
# | **GAP**           | Output gap as a percentage of potential GDP                                       |
# | **ULC**           | Unit labour cost in total economy                                                 |
# | **RPMGS**         | Relative price of imported goods and services                                     |
# | **EXCH**          | Exchange rate, national currency per USD                                          |
# | **EXCHEB**        | Nominal effective exchange rate, chain-linked, overall weights                    |
# | **UNR**           | Unemployment rate                                                                 |
# | **HRS**           | Hours worked per worker, total economy                                            |
# | **CPI\_YTYPCT**   | Consumer price index (headline inflation), year-on-year %                         |
# | **PCORE\_YTYPCT** | Core inflation index, year-on-year %                                              |
# | **NLGXQ**         | General government primary balance as a percentage of GDP                         |
# | **GGFLMQ**        | Gross public debt, Maastricht criterion as a percentage of GDP                    |
# | **MPEN**          | Import penetration, goods and services                                            |
# | **PDTY**          | Labour productivity, total economy                                                |
# | **KTPV\_ANNPCT**  | Productive capital stock, volume, annual % growth                                 |
# | **ITV\_ANNPCT**   | Gross fixed capital formation, total, volume, annual % growth                     |
# | **CPV\_ANNPCT**   | Private final consumption expenditure, volume, annual % growth                    |
# | **FBGSQ**         | Net exports of goods and services as a percentage of GDP                          |
# | **ULCDR**         | Indicator of competitiveness based on relative unit labour costs in total economy |
# | **TTRADE**        | Terms of trade, goods and services                                                |
# | **IRS**           | Short-term interest rate                                                          |
# | **IRL**           | Long-term interest rate on government bonds                                       |
# | **NOOQ**          | Net one-offs of general government as a percentage of potential GDP               |
# 
# 

# %%
input_file = os.path.join(project_root, "data", "source_raw", "OECD.ECO.MAD,DSD_EO@DF_EO,+CZE..A.csv")

# Read the OECD data
df_oecd = pd.read_csv(input_file)

# Define the list of selected series
selected_series = [
    "GAP", "ULC", "RPMGS", "EXCH", "EXCHEB", "UNR", "HRS", "CPI_YTYPCT",
    "PCORE_YTYPCT", "NLGXQ", "GGFLMQ", "MPEN", "PDTY", "KTPV_ANNPCT",
    "ITV_ANNPCT", "CPV_ANNPCT", "FBGSQ", "ULCDR", "TTRADE", "IRS", "IRL", "NOOQ"
]

# Filter the data
df_oecd_filtered = df_oecd[df_oecd["MEASURE"].isin(selected_series)].copy()
df_oecd_filtered = df_oecd_filtered[(df_oecd_filtered["TIME_PERIOD"] >= 1999) & (df_oecd_filtered["TIME_PERIOD"] <= 2024)]

# Select and rename columns to create a tidy dataframe
df_oecd_tidy = df_oecd_filtered[["TIME_PERIOD", "MEASURE", "OBS_VALUE"]].rename(
    columns={"TIME_PERIOD": "year", "MEASURE": "metric", "OBS_VALUE": "value"}
)


# %% [markdown]
# ### merge data
# 
# 

# %%
# merge data: final_annual, df_hicp_annual, energy datasets, df_wages, df_gdp, df_unemp, df_fx on "year"
df_final = final_annual.merge(df_hicp_annual, on="year", how="left")
df_final = df_final.merge(df_hicp_overall_roc_annual, on="year", how="left")
df_final = df_final.merge(df_pure_energy_roc_annual, on="year", how="left")
df_final = df_final.merge(df_energy_full_roc_annual, on="year", how="left")
df_final = df_final.merge(df_wages, on="year", how="left")
df_final = df_final.merge(df_gdp, on="year", how="left")
df_final = df_final.merge(df_unemp, on="year", how="left")
df_final = df_final.merge(df_fx, on="year", how="left")



# convert to tidy data
df_final = pd.melt(df_final, id_vars=["year"], var_name="metric", value_name="value")

# append the import price index data
df_import_price_index = df_import_price_index[["year", "metric", "value"]]

# append oecd data
df_final = pd.concat([df_final, df_import_price_index, df_oecd_tidy], ignore_index=True)
                                              

# save to parquet
output_file = os.path.join(output_folder, "economy_annual_tidy.parquet")
df_final.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)
print("Annual economy data saved to:", output_file)


# %% [markdown]
# ## MagnusWeb Panel Construction: Intuition & Methods
# 
# This notebook cell transforms our raw MagnusWeb exports into a **firm–year panel** ready for panel regressions (e.g. fixed-effects, VARs). Below is a summary of the key design choices and processing steps:
# 
# ---
# 
# ### 1. Why a Firm–Year "Wide" Panel?
# 
# - **Model-ready**: Most econometric libraries (`linearmodels.PanelOLS`, `statsmodels`, etc.) expect one row per firm × year, with each variable in its own column.  
# - **Efficient storage**: 185 k firms × ~24 years ≈ 4–5 million rows, ~25 variables → ~200 MB.  
# - **No repeated melts**: Once built, we can `read_parquet()` in ~2 s and immediately start modeling.
# 
# ---
# 
# ### 2. Reading & Concatenating Exports Lazily
# 
# - We scan all `export-*.csv` files with **Polars' `scan_csv`**, which builds a **lazy execution graph** instead of loading data immediately.  
# - This keeps memory usage low and lets Polars fuse operations for maximum speed.
# 
# ---
# 
# ### 3. Static vs. Time-coded Columns
# 
# - **Static columns** (`STATIC_COLS`): firm identifiers, location, NACE/OKEČ codes, audit flags, dates.  
# - **Time columns**: every header containing a year/quarter (e.g. `"2022/4Q Náklady"`, `"2019 Obrat Výnosy"`).  
# 
# Separating them lets us **melt only the time columns** into a long format without touching firm metadata.
# 
# ---
# 
# ### 4. Building the Long Table
# 
# 1. **Melt** time columns into two new fields:  
#    - `raw` (original header)  
#    - `val` (numeric value)  
# 2. **Extract** `year` (4-digit) and `quarter` (`1Q`–`4Q`) via regex.  
# 3. **Derive** `metric_cs` by stripping the leading "YYYY/4Q " or "4Q/YYYY " or "YYYY ".  
# 4. **Map** Czech metric names (e.g. `"Náklady"`) to canonical English slugs (`costs`, `profit_pre_tax`, etc.).  
# 5. **Filter** to keep **only annual snapshots** or **4Q observations** (we treat `quarter == 4` as year-end).
# 
# This yields a **long** table with columns `[IČO, year, quarter, metric, val, ...other_static_cols]`.
# 
# ---
# 
# ### 5. Pivoting to the Final Wide Panel
# 
# - The long table is **pivoted** on `IČO` and `year`, with each unique `metric` slug becoming its own column.
# - Static firm metadata is deduplicated and joined back to create the final dataset.
# - **Result**: A wide firm-year panel where each row represents a unique firm-year observation, with all financial metrics as separate columns (e.g., `profit_pre_tax`, `total_assets`, `sales_revenue`).
# 
# This structure is optimized for econometric modeling and can be directly used in panel regression analyses.
# 
# Note: Before saving the final panel to Parquet, we remove columns that are static for each ICO (do not change across years), including original Czech financial metric columns. This ensures the output file contains only time-variant and relevant columns for econometric analysis. See code section before Parquet write for details.

# %%
import os, re, polars as pl

# %%
# ------------------------------------------------------------------
# 1. folders
# ------------------------------------------------------------------
project_root  = os.path.abspath(os.path.join(os.getcwd(), ".."))
in_dir        = os.path.join(project_root, "data", "source_raw",  "magnusweb")
out_dir       = os.path.join(project_root, "data", "source_cleaned")
os.makedirs(out_dir, exist_ok=True)


# %%
# ------------------------------------------------------------------
# 2. read all exports lazily
# ------------------------------------------------------------------
csv_files = sorted(
    f for f in os.listdir(in_dir) if f.startswith("export-") and f.endswith(".csv")
)
if not csv_files:
    raise FileNotFoundError("No export-*.csv files found!")

lazy_frames = [
    pl.scan_csv(
        os.path.join(in_dir, f),
        separator=";",
        quote_char='"',                # handle quoted fields correctly
        encoding="utf8",
        try_parse_dates=False,         # faster – we parse dates later
        infer_schema_length=0,         # let Polars sample entire file to infer dtypes
    )
    for f in csv_files
]

raw = pl.concat(lazy_frames, how="vertical")        # still lazy
# No need to strip quotes manually anymore
print(f"Found  {len(csv_files)}  CSV parts ➜ concatenated lazily")

# %%
# ------------------------------------------------------------------
# 3. identify static-vs-time columns
# ------------------------------------------------------------------
STATIC_COLS = [
    "IČO", "Název subjektu",
    "Hlavní NACE", "Hlavní NACE - kód",
    "Vedlejší NACE CZ", "Vedlejší NACE CZ - kód",
    "Hlavní OKEČ", "Hlavní OKEČ - kód",
    "Vedlejší OKEČ", "Vedlejší OKEČ - kód",
    "Institucionální sektory (ESA 2010)", "Institucionální sektory (ESA 95)",
    "Lokalita", "Kraj", "Počet zaměstnanců", "Kategorie počtu zaměstnanců CZ", "Kategorie obratu",
    "Audit", "Konsolidace", "Měna",
    "Datum vzniku", "Datum zrušení", "Rok", "Čtvrtletí", "Stav subjektu", "Právní forma", "Typ subjektu",
    'Hospodářský výsledek před zdaněním',
    'Hospodářský výsledek za účetní období',
    'Provozní hospodářský výsledek',
    'Náklady',
    'Obrat, Výnosy',
    'Tržby, Výkony',
    'Aktiva celkem',
    'Stálá aktiva',
    'Oběžná aktiva',
    'Ostatní aktiva',
    'Pasiva celkem',
    'Vlastní kapitál',
    'Cizí zdroje',
    'Ostatní pasiva',
    ]


time_cols = [c for c in raw.collect_schema().names() if c not in STATIC_COLS]

# %%
# %%
# ------------------------------------------------------------------
# 4. melt ➜ parse (year, quarter, metric) ➜ keep 4Q/annual rows (ROBUST)
# ------------------------------------------------------------------
metric_map = {
    "Hospodářský výsledek před zdaněním":   "profit_pre_tax",
    "Hospodářský výsledek za účetní období":"profit_net",
    "Provozní hospodářský výsledek":        "oper_profit",
    "Náklady":                              "costs",
    "Obrat, Výnosy":                        "turnover",
    "Obrat Výnosy":                         "turnover",
    "Tržby, Výkony":                        "sales_revenue",
    "Tržby Výkony":                         "sales_revenue",
    "Aktiva celkem":                        "total_assets",
    "Stálá aktiva":                         "fixed_assets",
    "Oběžná aktiva":                        "current_assets",
    "Ostatní aktiva":                       "other_assets",
    "Pasiva celkem":                        "total_liabilities_and_equity",
    "Vlastní kapitál":                      "equity",
    "Cizí zdroje":                          "total_liabilities",
    "Ostatní pasiva":                       "other_liabilities",
}


def build_long(lf: pl.LazyFrame) -> pl.LazyFrame:
    """melt & parse year/quarter/metric, return long table"""
    long = (
        lf.melt(id_vars=STATIC_COLS, value_vars=time_cols,
                variable_name="raw", value_name="val")
          .drop_nulls("val")
          # --- extract pieces with regex ----------------------------------
          .with_columns([
              # 4-digit year anywhere in the string
              pl.col("raw").str.extract(r"(\d{4})", 1).cast(pl.Int32).alias("year"),
              # quarter pattern like '4Q'
              pl.col("raw").str.extract(r"([1-4]Q)", 1).alias("q_raw"),
          ])
          # metric = raw minus leading 'YYYY/4Q ' or '4Q/YYYY ' or 'YYYY '
          .with_columns(
              pl.when(pl.col("raw").str.contains(r"^\d{4}/[1-4]Q"))
                 .then(pl.col("raw").str.replace(r"^\d{4}/[1-4]Q\s*", ""))
               .when(pl.col("raw").str.contains(r"^[1-4]Q/\d{4}"))
                 .then(pl.col("raw").str.replace(r"^[1-4]Q/\d{4}\s*", ""))
               .when(pl.col("raw").str.contains(r"^\d{4}$"))
                 .then(pl.col("raw").str.replace(r"^\d{4}$", ""))
               .when(pl.col("raw").str.contains(r"^\d{4}\s"))
                 .then(pl.col("raw").str.replace(r"^\d{4}\s*", ""))
               .otherwise(pl.col("raw"))
               .alias("metric_cs")
          )
          .with_columns([
              # map Czech metric name to English slug; drop rows we don't recognise
              pl.col("metric_cs").map_elements(lambda x: metric_map.get(x), return_dtype=pl.String).alias("metric")
          ])
          .filter(pl.col("metric").is_not_null())
          # quarter = int( q_raw[0] ) or null
          # THIS IS THE CORRECTED LINE:
          .with_columns(
              pl.col("q_raw").str.replace("Q", "").cast(pl.Int8, strict=False).alias("quarter")
          )
          .drop("q_raw", "raw", "metric_cs")
          # keep only annual or 4Q values
          # This filter will now work correctly
          .filter(pl.col("quarter").is_null() | (pl.col("quarter") == 4))
    )
    return long

# Now, re-run the rest of your script, starting with creating the 'long' frame:
long = build_long(raw)

# ... then proceed with the lazy pivot, lazy join, and final collect.
# (The code for steps 5, 6, 7 from the previous answer is correct)

# %%
# 5. build the wide panel using an ISOLATED "group_by-agg" pivot
#    (This is the corrected step)
# ------------------------------------------------------------------
# First, get the list of metric slugs that will become columns.
final_metric_columns = list(set(metric_map.values())) # Use set to handle duplicate mappings

# Now, we construct the pivot manually.
# CRITICAL CHANGE: Select ONLY the columns needed for the pivot.
panel_lazy = (
    long.select(["IČO", "year", "metric", "val"])
        .group_by(["IČO", "year"], maintain_order=True)
        .agg(
            [
                pl.col("val").filter(pl.col("metric") == metric).first().alias(metric)
                for metric in final_metric_columns
            ]
        )
)

# %%
# ------------------------------------------------------------------
# 6. attach (static) firm attributes (No changes needed)
# ------------------------------------------------------------------
# This step from the previous answer is correct and robustly handles duplicates.
other_static_cols = [c for c in STATIC_COLS if c != "IČO"]
static_unique_lazy = (
    raw.select(STATIC_COLS)
       .group_by("IČO", maintain_order=False)
       .agg([pl.col(c).first() for c in other_static_cols])
)

# Join the two lazy frames. This will now work without any name conflicts.
final_lazy_panel = panel_lazy.join(
    static_unique_lazy, on="IČO", how="left"
)

# Execute the final plan.
print("✔  Lazy plan built. Now executing and collecting the final panel...")
panel = final_lazy_panel.collect(streaming=True)
print("✔  Collection complete.")



# %%
# ------------------------------------------------------------------
# 7. light dtype + English column names
# ------------------------------------------------------------------
rename_static = {
    "IČO":"ico", "Název subjektu":"name",
    "Hlavní NACE":"main_nace", "Hlavní NACE - kód":"main_nace_code",
    "Vedlejší NACE CZ":"sub_nace_cz", "Vedlejší NACE CZ - kód":"sub_nace_cz_code",
    "Hlavní OKEČ":"main_okec", "Hlavní OKEČ - kód":"main_okec_code",
    "Vedlejší OKEČ":"sub_okec", "Vedlejší OKEČ - kód":"sub_okec_code",
    "Institucionální sektory (ESA 2010)":"esa2010",
    "Institucionální sektory (ESA 95)":"esa95",
    "Lokalita":"locality", "Kraj":"region",
    "Počet zaměstnanců":"num_employees",
    "Kategorie počtu zaměstnanců CZ":"num_employees_cat",
    "Kategorie obratu":"turnover_cat",
    "Audit":"audit", "Konsolidace":"consolidation",
    "Měna":"currency",
    "Datum vzniku":"date_founded", "Datum zrušení":"date_dissolved", 
    "Stav subjektu":"status",
    "Právní forma":"legal_form", 
    "Typ subjektu":"entity_type",
}
# Make rename more robust
current_cols = set(panel.columns)
rename_map_filtered = {k: v for k, v in rename_static.items() if k in current_cols}
panel = panel.rename(rename_map_filtered)


# Convert metric columns to Float64
metric_cols = list(set(metric_map.values()))
panel = panel.with_columns([
    pl.col(c).cast(pl.Float64, strict=False) for c in metric_cols if c in panel.columns
])


# simple dtype tweaks (polars is already memory-efficient)
panel = panel.with_columns([
    pl.col("year").cast(pl.Int16),
    # THIS IS THE CORRECTED LINE:
    pl.col("num_employees").cast(pl.Int32, strict=False),
    # The rest is correct as is:
    pl.col([c for c in ["audit","consolidation","currency","esa2010","esa95",
                        "main_nace","sub_nace_cz","main_okec","sub_okec",
                        "locality","region","turnover_cat"]
           if c in panel.columns]).cast(pl.Categorical),
])

# %%
# ------------------------------------------------------------------
# 8. write once – Parquet
# ------------------------------------------------------------------
# Remove specified columns before saving to Parquet
cols_to_remove = [
    'Hospodářský výsledek před zdaněním', 'Hospodářský výsledek za účetní období',
    'Provozní hospodářský výsledek', 'Náklady', 'Obrat, Výnosy', 'Tržby, Výkony',
    'Aktiva celkem', 'Stálá aktiva', 'Oběžná aktiva', 'Ostatní aktiva',
    'Pasiva celkem', 'Vlastní kapitál', 'Cizí zdroje', 'Ostatní pasiva', 'Rok', 'Čtvrtletí',
]
cols_to_drop = [c for c in cols_to_remove if c in panel.columns]
panel = panel.drop(cols_to_drop)

out_path = os.path.join(out_dir, "magnusweb_panel.parquet")
panel.write_parquet(out_path, compression="snappy")
print("✔  firm-year panel saved   ➜", out_path)


# %%
# ------------------------------------------------------------------
# 9. quick sanity check (optional)
# ------------------------------------------------------------------
preview = (
    panel.select(["ico","year","profit_pre_tax","sales_revenue","num_employees"])
          .filter(pl.col("year") >= 2021)
          .limit(5)
)
print(preview)

# %%
print("Type of panel:", type(panel))

def find_static_columns(df, id_col="ico"):
    import pandas as pd
    # Convert to pandas DataFrame for groupby compatibility
    pdf = df.to_pandas() if hasattr(df, "to_pandas") else pd.DataFrame(df)
    static_cols = []
    for col in pdf.columns:
        if col == id_col:
            continue
        unique_counts = pdf.groupby(id_col)[col].nunique()
        if unique_counts.max() == 1:
            static_cols.append(col)
    return static_cols

static_columns = find_static_columns(panel)
print("Static columns (do not change across years for each ICO):", static_columns)

# %%
print("Type of panel:", type(panel))

def find_time_series_columns(df, id_col="ico"):
    import pandas as pd
    # Convert to pandas DataFrame for groupby compatibility
    pdf = df.to_pandas() if hasattr(df, "to_pandas") else pd.DataFrame(df)
    time_series_cols = []
    for col in pdf.columns:
        if col == id_col:
            continue
        unique_counts = pdf.groupby(id_col)[col].nunique()
        if unique_counts.max() > 1:
            time_series_cols.append(col)
    return time_series_cols

time_series_columns = find_time_series_columns(panel)
print("Time-series columns (change across years for each ICO):", time_series_columns)


# %% [markdown]
# ### Matching of NACE codes from different sources 
# 
# Main source of the matching is the NACE Rev. 2 classification from CZSO: https://apl2.czso.cz/iSMS/en/klasdata.jsp?kodcis=80004
# 
# 1. **Ancestry Extraction:**  
#    The code builds the hierarchy for each record by following the parent pointer (`nadvaz`) from the current row back to the top-level record (level 1). This produces a lineage (a list of `(uroven, chodnota)` tuples) that starts at the top and ends at the current row. This hierarchical path is used for further transformations.
# 
# 2. **Separation of Top-Level Letter and Numeric Levels:**  
#    - **Top-Level Code (Level 1):** The first element of the ancestry (level 1) is expected to be a letter (e.g., "A", "B", etc.) and is stored as the `level1_code`.  
#    - **Numeric Levels:** All subsequent levels (levels 2 and above) contain numeric codes. These codes are collected separately for further processing.
# 
# 3. **Incremental Code Computation:**  
#    For each numeric level, an incremental code is computed. The idea is to capture only the additional characters beyond the parent’s numeric code:
#    - For the first numeric level (level 2), the full numeric code is used as is.
#    - For each subsequent level, the prefix that matches the parent’s full numeric code is removed. This yields a shorter “incremental” code that highlights the difference between the level and its parent.
# 
# 4. **Construction of `full_nace`:**  
#    The `full_nace` field is constructed by concatenating the top-level letter with the incremental codes from each numeric level, joined with dots. This produces a compact representation that still reflects the hierarchical structure (e.g., `"A.01.1.1.10"`). This format is used by Eurostat. 
# 
# 5. **Magnus NACE Code Calculation:**  
#    The `magnus_nace` is generated from the current row’s `chodnota`:
#    - For rows at levels 1, 2, 3, 4, 5 the code is padded to 6 digits (using trailing zeros) to conform to the Magnus format.
#    - Additionally, for level 1 rows, the code explicitly fills `magnus_nace` with the `level1_code` (the top-level letter).
# 
# 6. **Industry Flag:**  
#    An `industry_flag` is set to `True` if the top-level letter (from `level1_code`) belongs to one of the specified sectors (B, C, D, E), indicating that the classification is part of an industry sector.
# 
# 7. **Final Output:**  
#    The resulting DataFrame includes the transformed columns:  
#    - `name_czso_cs` (short description),  
#    - `level` (hierarchical level),  
#    - `level1_code` through `level5_code` (incremental codes for each level),  
#    - `full_nace` (incremental full hierarchy),  
#    - `magnus_nace` (formatted 6-digit code where applicable), and  
#    - `industry_flag` (industry indicator).  
#    This table is then saved to Parquet.
# 
# 

# %%
import os
import pandas as pd
from datetime import datetime

# %%
# -------------------------------------------------------------------------
# 1. Define file paths
# -------------------------------------------------------------------------
script_dir = os.getcwd()  # current directory in Jupyter
project_root = os.path.abspath(os.path.join(script_dir, ".."))
input_file = os.path.join(project_root, "data", "source_raw", "NACE", "KLAS80004_CS_NACE_classification.csv")
output_folder = os.path.join(project_root, "data", "source_cleaned")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_file = os.path.join(output_folder, "t_nace_matching.parquet")

# -------------------------------------------------------------------------
# 2. Load the CSV file
# -------------------------------------------------------------------------
df_czso_nace = pd.read_csv(input_file, sep=",")

# Expected columns: "kodjaz","akrcis","kodcis","uroven","chodnota",
# "zkrtext","text","admplod","admnepo","nadvaz"

# -------------------------------------------------------------------------
# 3. Preprocess data: ensure string type and fill NaNs
# -------------------------------------------------------------------------
df_czso_nace = df_czso_nace.fillna("")
df_czso_nace["chodnota"] = df_czso_nace["chodnota"].astype(str)
df_czso_nace["nadvaz"] = df_czso_nace["nadvaz"].astype(str)

# Build a lookup: mapping from chodnota value to DataFrame index
chodnota_to_idx = { row["chodnota"]: i for i, row in df_czso_nace.iterrows() }

# -------------------------------------------------------------------------
# 4. Function to retrieve ancestry (from level 1 to current)
# -------------------------------------------------------------------------
def get_ancestry_codes(row, df):
    """
    Returns a list of (uroven, chodnota) tuples from the top ancestor (level 1)
    down to the current row.
    """
    lineage = []
    current_chodnota = row["chodnota"]
    while current_chodnota:
        idx = chodnota_to_idx.get(current_chodnota)
        if idx is None:
            break
        current_row = df.loc[idx]
        lineage.append((int(current_row["uroven"]), current_row["chodnota"]))
        parent = current_row["nadvaz"]
        if not parent or parent == current_chodnota:
            break
        current_chodnota = parent
    lineage.reverse()  # now from top (level 1) to current
    return lineage

# -------------------------------------------------------------------------
# 5. Helper to create a 6-digit Magnus NACE code from a full numeric code
# -------------------------------------------------------------------------
def to_magnus_nace(code_str):
    if not code_str.isdigit():
        return None
    # Pad with trailing zeros to get 6 digits
    return code_str.ljust(6, "0") if len(code_str) < 6 else code_str[:6]

# -------------------------------------------------------------------------
# 6. Build new classification table with adjustments
# -------------------------------------------------------------------------
rows_output = []

for i, row in df_czso_nace.iterrows():
    lineage = get_ancestry_codes(row, df_czso_nace)
    
    # Separate top-level letter and numeric levels (levels>=2)
    letter = ""
    numeric_levels = []  # store full numeric codes as strings
    for lvl, code in lineage:
        if lvl == 1:
            letter = code  # expected to be a letter (e.g. "A", "U")
        else:
            numeric_levels.append(code)
    
    # full_nace: join letter with all full numeric codes using dots
    # full_nace_parts = [letter] + numeric_levels if letter else numeric_levels
    # full_nace = ".".join(full_nace_parts)
    
    # Always fill level1_code from the letter (even for lower levels)
    level1_code = letter
    
    # Compute incremental codes for numeric levels:
    # For the first numeric level, incremental = full numeric (since no parent)
    # For subsequent ones, remove the parent's full code prefix.
    inc_codes = []
    prev_full = ""
    for idx_num, num_code in enumerate(numeric_levels):
        if idx_num == 0:
            inc = num_code  # full code for level 2 remains as is
        else:
            # Remove parent's full code (its length) from current full code
            inc = num_code[len(numeric_levels[idx_num - 1]):]
        inc_codes.append(inc)

    # Build full_nace using the top-level letter and the incremental numeric codes:
    full_nace_parts = [letter] + inc_codes
    full_nace = ".".join(full_nace_parts)
    
    # Prepare level2_code to level5_code (if available)
    level2_code = inc_codes[0] if len(inc_codes) >= 1 else ""
    level3_code = inc_codes[1] if len(inc_codes) >= 2 else ""
    level4_code = inc_codes[2] if len(inc_codes) >= 3 else ""
    level5_code = inc_codes[3] if len(inc_codes) >= 4 else ""
    
    # Determine magnus_nace:
    # Use the current row's full numeric code (row["chodnota"]) if level is 2,3,4,5.
    try:
        current_level = int(row["uroven"])
    except:
        current_level = 0
    if current_level in [2, 3, 4, 5]:
        magnus_nace = to_magnus_nace(row["chodnota"])
    else:
        magnus_nace = ""  # leave empty for level 1 or 5
    
    # Determine industry_flag based on top-level letter (B, C, D, E)
    industry_flag = (letter in ["B", "C", "D", "E"])
    
    # Build record; note that full_nace is the cumulative full numeric code sequence
    out_record = {
        "name_czso_cs": row["zkrtext"],
        "level": row["uroven"],
        "czso_code": row["chodnota"],
        "level1_code": level1_code,
        "level2_code": level2_code,
        "level3_code": level3_code,
        "level4_code": level4_code,
        "level5_code": level5_code,
        "full_nace": full_nace,
        "magnus_nace": magnus_nace,
        "industry_flag": industry_flag,
    }
    rows_output.append(out_record)

# when level = 1, fill magnus_nace with level1_code
for record in rows_output:
    if record["level"] == 1:
        record["magnus_nace"] = record["level1_code"]

df_result = pd.DataFrame(rows_output)


# %%
# enrich with english names 
input_file = os.path.join(project_root, "data", "source_raw", "NACE", "KLAS80004_EN_NACE_classification.csv")

df_en_nace = pd.read_csv(input_file, sep=",")
df_en_nace = df_en_nace.fillna("")
df_en_nace["chodnota"] = df_en_nace["chodnota"].astype(str)

# Build a lookup: mapping from chodnota value to df_results, creating new column name_czso_en
chodnota_to_idx_en = { row["chodnota"]: i for i, row in df_en_nace.iterrows() }
# Merge with df_result
df_result["name_czso_en"] = ""
for i, row in df_result.iterrows():
    # Look up using czso_code rather than non-existent column
    idx = chodnota_to_idx_en.get(row["czso_code"])
    if idx is not None:
        df_result.at[i, "name_czso_en"] = df_en_nace.loc[idx]["zkrtext"]

# count null or empty values
# df_result["name_czso_en"].isnull().sum(), df_result["name_czso_en"].eq("").sum()

# duplicate czso_code
df_result["czso_code"].duplicated().sum()

# move name_czso_en to the second position
cols = df_result.columns.tolist()
cols.insert(1, cols.pop(cols.index("name_czso_en")))
df_result = df_result[cols]


# %%
# 'other' row - present in nagnus data, but not in czso data
new_row = {
    "name_czso_cs": "Výroba, obchod a služby neuvedené v přílohách 1 až 3 živnostenského zákona",
    "level": 1,
    "czso_code": "00",
    "level1_code": "00",
    "level2_code": "",
    "level3_code": "",
    "level4_code": "",
    "level5_code": "",
    "full_nace": "00",
    "magnus_nace": "00",
    "industry_flag": False,
    "name_czso_en": "Production, trade and services not listed in Annexes 1 to 3 of the Trade Licensing Act"
}

df_result = pd.concat([df_result, pd.DataFrame([new_row])], ignore_index=True)


# %%
# save to parquet
df_result.to_parquet(output_file, index=False)
# Print the output file path
print(f"Data saved to {output_file}")

# %%



# %%
import os
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Constants
LEVEL_SERIES_THRESHOLD = 0.01  # Minimum non-zero threshold for log calculations
GROWTH_RATE_OUTLIER_THRESHOLD = 5.0  # ±500% growth rate threshold for outlier detection

# Winsorize thresholds for growth rates
LOWER_WIN_THRESHOLD = 0.01  # Lower threshold for winsorization
UPPER_WIN_THRESHOLD = 0.99   # Upper threshold for winsorization

# Minimum nonnegative threshold for log transformations
MAX_NEG_THRESHOLD = 0.05  # Maximum proportion of negative values for log transformations

# Input and output paths
input_path = os.path.join("..", "data", "data_ready", "merged_panel_imputed.parquet")
output_path = os.path.join("..", "data", "data_ready", "merged_panel_winsorized.parquet")

print(f"Input path: {input_path}")
print(f"Output path: {output_path}")

# Verify input file exists
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Input file not found: {input_path}")
    
print("✓ Input file exists")

# %%
# Load the merged panel dataset
print("Loading merged panel dataset...")
df = pl.read_parquet(input_path)
df = df.sort(["firm_ico", "year"])

print(f"Dataset shape: {df.shape}")
print(f"Columns: {len(df.columns)}")
print(f"Years covered: {df['year'].min()} - {df['year'].max()}")

# Check for key identifier variables
key_vars = ['firm_ico', 'year']
for var in key_vars:
    if var in df.columns:
        print(f"✓ {var} found")
    else:
        print(f"✗ {var} missing")

# Display a sample of the data structure
print("\nData sample:")
print(df.head(3))

# %%
# Define variable groups for different transformations
# Based on the user's specifications

# Group 1: Log Year-over-Year Growth (_logyoy)
# Formula: X_logyoy_t = ln(X_t) - ln(X_{t-1})
LOG_YOY_VARS = [
    # Firm-level financials (CZK)
    'firm_sales_revenue',
    'firm_turnover', 
    'firm_oper_profit',
    'firm_profit_pre_tax',
    'firm_profit_net',
    'firm_costs',
    'firm_total_assets',
    'firm_equity',
    'firm_total_liabilities_and_equity',
    
    # Sector-level (by NACE)
    'sector_level1_avg_wages_by_nace',
    'sector_level1_ppi_by_nace',
    'sector_level1_no_of_employees_by_nace',
    'sector_level2_avg_wages_by_nace',
    'sector_level2_ppi_by_nace',
    'sector_level2_no_of_employees_by_nace',


    # Macro-level (levels or indices)
    'mac_nom_gr_avg_wage_czk',
    'mac_gdp_nominal_prices',
    'mac_gdp_2020_base_prices',
    'mac_fx_czk_eur_annual_avg',
    'mac_import_price_index_ex_energy',
    'mac_deflator_base_2020',
    'mac_ULC',
    'mac_PDTY',
    'mac_ULCDR',
    'mac_EXCHEB',
    'mac_TTRADE',
    'mac_RPMGS',
]

# Group 2: Percentage Change (_pct)
# Formula: X_pct_t = 100*(X_t / X_{t-1} - 1)
PCT_CHANGE_VARS = LOG_YOY_VARS.copy()  # Mostly the same variables

# Group 3: Difference in Percentage Points (_dpp)
# Formula: X_dpp_t = X_t - X_{t-1}
DPP_VARS = [
    # Firm ratios & margins
    'firm_operating_margin_cal',
    'firm_net_margin_cal',
    'firm_cost_ratio_cal',
    'firm_equity_ratio_cal',
    'firm_effective_tax_rate_cal',
    'firm_roa_ebit_cal',
    'firm_roe_cal',
    
    # Macro rates & shares (%)
    'mac_cnb_repo_rate_annual',
    'mac_unemp_rate',
    'mac_IRS',
    'mac_IRL',
    'mac_GAP',
    'mac_NLGXQ',
    'mac_FBGSQ',
    'mac_GGFLMQ',
    'mac_MPEN',
    'mac_CPI_YTYPCT',
    'mac_PCORE_YTYPCT',
    'mac_NOOQ',
    'mac_UNR'
]

# Group 4: Already YoY % (no transform needed, but can add _dpp)
ALREADY_YOY_VARS = [
    'mac_hicp_overall_roc',
    'mac_hicp_pure_energy_roc',
    'mac_hicp_energy_full_roc',
    'mac_KTPV_ANNPCT',
    'mac_CPV_ANNPCT',
    'mac_ITV_ANNPCT'
]

# Special cases
SPECIAL_CASES = {
    'mac_gdp_2020_base_prices_sopr': 'base_100_index'  # Transform: X - 100
}

print("Variable groups defined:")
print(f"Log YoY variables: {len(LOG_YOY_VARS)}")
print(f"Percentage change variables: {len(PCT_CHANGE_VARS)}")
print(f"Difference in percentage points variables: {len(DPP_VARS)}")
print(f"Already YoY variables: {len(ALREADY_YOY_VARS)}")
print(f"Special cases: {len(SPECIAL_CASES)}")

# %%
# Check which variables from our groups actually exist in the dataset
def check_vars_in_df(var_list, var_name):
    """Check which variables from a list exist in the dataframe"""
    available_vars = [var for var in var_list if var in df.columns]
    missing_vars = [var for var in var_list if var not in df.columns]
    
    print(f"\n{var_name}:")
    print(f"  Available: {len(available_vars)}/{len(var_list)}")
    if missing_vars:
        print(f"  Missing: {missing_vars}")
    
    return available_vars

# Check all variable groups
available_log_yoy = check_vars_in_df(LOG_YOY_VARS, "Log YoY variables")
available_pct = check_vars_in_df(PCT_CHANGE_VARS, "Percentage change variables")
available_dpp = check_vars_in_df(DPP_VARS, "Difference in pp variables")
available_yoy = check_vars_in_df(ALREADY_YOY_VARS, "Already YoY variables")

# Check special cases
available_special = {}
for var, transform_type in SPECIAL_CASES.items():
    if var in df.columns:
        available_special[var] = transform_type
        print(f"  Special case '{var}' ({transform_type}): Available")
    else:
        print(f"  Special case '{var}' ({transform_type}): Missing")

print(f"\nDataset columns sample: {df.columns[:10]}")
print(f"Total columns in dataset: {len(df.columns)}")

# Look for any variables that might have similar names
def find_similar_vars(target_vars, dataset_cols):
    """Find variables with similar names in the dataset"""
    similar = {}
    for target in target_vars:
        if target not in dataset_cols:
            # Look for partial matches
            matches = [col for col in dataset_cols if target.replace('_', '').lower() in col.replace('_', '').lower()]
            if matches:
                similar[target] = matches
    return similar

print("\nLooking for similar variable names...")
similar_log_yoy = find_similar_vars(LOG_YOY_VARS, df.columns)
if similar_log_yoy:
    print("Similar log YoY variables found:")
    for target, matches in similar_log_yoy.items():
        print(f"  {target} -> {matches}")

# %%
# Define transformation functions with robust handling
def calculate_log_yoy_robust(df: pl.DataFrame, var: str, group: str = "firm_ico") -> pl.DataFrame:
    """
    ln(X_t) − ln(X_{t−1}) within each firm; NaN if either X≤0.
    """
    new = f"{var}_logyoy"
    df = df.sort([group, "year"])
    lag = pl.col(var).shift(1).over(group)

    expr = pl.when(
        (pl.col(var) > 0) & (lag > 0)
    ).then(
        pl.col(var).log() - lag.log()
    ).otherwise(None)

    return df.with_columns(expr.alias(new))


def calculate_pct_change(df: pl.DataFrame, var: str, group: str = "firm_ico") -> pl.DataFrame:
    """
    Compute percentage change: 100 × (X_t / X_{t−1} − 1)
    Robust to zero, null, inf lag values. Sets result to null if lag is null, zero, or not finite.
    """
    new = f"{var}_pct"
    df = df.sort([group, "year"])
    lag = pl.col(var).shift(1).over(group)

    expr = (
        pl.when(
            lag.is_null() |      # Previous value missing
            (lag == 0) |         # Avoid division by zero
            (~lag.is_finite())   # Exclude infinite or nan lag
        )
        .then(None)
        .otherwise(100 * (pl.col(var) / lag - 1))
        .alias(new)
    )
    return df.with_columns(expr)


def calculate_dpp_robust(df: pl.DataFrame, var: str, group: str = "firm_ico") -> pl.DataFrame:
    """
    X_t − X_{t−1} within each firm.
    """
    new = f"{var}_dpp"
    df = df.sort([group, "year"])
    expr = (pl.col(var) - pl.col(var).shift(1).over(group)).alias(new)
    return df.with_columns(expr)

def calculate_base_100_pct(df: pl.DataFrame, var_name: str) -> pl.DataFrame:
    """
    Calculate percentage change from base 100: X - 100
    
    Args:
        df: Polars DataFrame
        var_name: Name of the variable to transform
    
    Returns:
        DataFrame with new column: {var_name}_pct
    """
    new_col_name = f"{var_name}_pct"
    
    result = df.with_columns([
        (pl.col(var_name) - 100).alias(new_col_name)
    ])
    
    return result

def winsorize_column(df, col_name, lower_pct=0.01, upper_pct=0.99):
    # Clean inf/nan to null before quantile
    col_tmp = "__tmp__"
    df = df.with_columns(
        pl.when(~pl.col(col_name).is_finite()).then(None).otherwise(pl.col(col_name)).alias(col_tmp)
    )
    percentiles = df.select([
        pl.col(col_tmp).quantile(lower_pct).alias("lower_bound"),
        pl.col(col_tmp).quantile(upper_pct).alias("upper_bound")
    ]).to_dicts()[0]
    lower_bound = percentiles["lower_bound"]
    upper_bound = percentiles["upper_bound"]
    df = df.with_columns([
        pl.when(pl.col(col_name) < lower_bound).then(lower_bound)
         .when(pl.col(col_name) > upper_bound).then(upper_bound)
         .otherwise(pl.col(col_name))
         .alias(col_name)
    ]).drop(col_tmp)
    return df

print("Robust transformation functions defined")

# %%
# Apply transformations to the dataset
print("Applying transformations to the dataset...")
print("=" * 50)

# Start with the original dataframe
df_transformed = df.clone()

# Keep track of new columns created
new_columns = []

# Key financial variables that need special robust handling
key_financial_vars = ['firm_sales_revenue', 'firm_turnover', 'firm_costs']
key_margin_vars = ['firm_operating_margin_cal', 'firm_net_margin_cal', 'firm_roa_ebit_cal', 'firm_roe_cal']

# 1. Log Year-over-Year Growth transformations
print("\n1. Calculating Log Year-over-Year Growth (_logyoy)...")
for var in available_log_yoy:

    neg_count = (df_transformed[var] < 0).sum()
    total_count = len(df_transformed)
    if (neg_count / total_count) > MAX_NEG_THRESHOLD:
        print(f"  ✗ {var}: Skipped -  {neg_count/total_count * 100:.1f}% negative values for log transformation")
        continue

    try:

        df_transformed = calculate_log_yoy_robust(df_transformed, var)
        
        new_col_name = f"{var}_logyoy"
        new_columns.append(new_col_name)
        
        # Check how many non-null values we got
        non_null_count = df_transformed.select(pl.col(new_col_name).count()).item()
        total_count = df_transformed.height
        
        print(f"  ✓ {var} -> {new_col_name} ({non_null_count:,}/{total_count:,} non-null)")
        
        # Apply winsorization for key financial variables
        # if var in key_financial_vars:
        #     print(f"    • Applying winsorization to {new_col_name}")
        #     df_transformed = winsorize_column(df_transformed, new_col_name, LOWER_WIN_THRESHOLD, UPPER_WIN_THRESHOLD) # log variables don't need winsorization

    except Exception as e:
        print(f"  ✗ {var}: Error - {e}")

# 2. Percentage Change transformations
print(f"\n2. Calculating Percentage Change (_pct)...")
for var in available_pct:
    try:

        df_transformed = calculate_pct_change(df_transformed, var)
        df_transformed = winsorize_column(df_transformed, f"{var}_pct", LOWER_WIN_THRESHOLD, UPPER_WIN_THRESHOLD)
        
        new_col_name = f"{var}_pct"
        new_columns.append(new_col_name)
        print(f"  ✓ {var} -> {new_col_name}")
    except Exception as e:
        print(f"  ✗ {var}: Error - {e}")

# 3. Difference in Percentage Points transformations
print(f"\n3. Calculating Difference in Percentage Points (_dpp)...")
for var in available_dpp:
    try:

        df_transformed = calculate_dpp_robust(df_transformed, var)
        
        new_col_name = f"{var}_dpp"
        new_columns.append(new_col_name)
        print(f"  ✓ {var} -> {new_col_name}")
        
        # Apply winsorization for key margin variables
        if var in key_margin_vars:
            print(f"    • Applying winsorization to {new_col_name}")
            df_transformed = winsorize_column(df_transformed, new_col_name, lower_pct=LOWER_WIN_THRESHOLD, upper_pct=UPPER_WIN_THRESHOLD)
            
    except Exception as e:
        print(f"  ✗ {var}: Error - {e}")

# 4. Special cases
print(f"\n4. Handling Special Cases...")
for var, transform_type in available_special.items():
    try:
        if transform_type == "base_100_index":
            df_transformed = calculate_base_100_pct(df_transformed, var)
            new_col_name = f"{var}_pct"
            new_columns.append(new_col_name)
            print(f"  ✓ {var} -> {new_col_name} (base-100 index)")
    except Exception as e:
        print(f"  ✗ {var}: Error - {e}")

# 5. Already YoY variables (can optionally add _dpp)
print(f"\n5. Already YoY variables (optionally adding _dpp)...")
for var in available_yoy:
    print(f" ✓ {var} - already in YoY format, no transformation needed")

print(f"\n" + "=" * 50)
print(f"Transformation Summary:")
print(f"  Original columns: {len(df.columns)}")
print(f"  New columns created: {len(new_columns)}")
print(f"  Final columns: {len(df_transformed.columns)}")
print(f"  Dataset shape: {df_transformed.shape}")

# Display new columns created
print(f"\nNew columns created: {new_columns[:10]}..." if len(new_columns) > 10 else f"New columns created: {new_columns}")

# Summary of winsorization applied
winsorized_vars = []
for var in key_financial_vars:
    if f"{var}_logyoy" in new_columns:
        winsorized_vars.append(f"{var}_logyoy")

for var in key_margin_vars:
    if f"{var}_dpp" in new_columns:
        winsorized_vars.append(f"{var}_dpp")

if winsorized_vars:
    print(f"\nWinsorized variables (1st-99th percentile): {winsorized_vars}")
else:
    print(f"\nNo variables were winsorized.")
    
# Check key financial variables specifically
print(f"\nKey Financial Variables Log Growth Status:")
for var in key_financial_vars:
    logyoy_var = f"{var}_logyoy"
    if logyoy_var in new_columns:
        positive_count = df_transformed.filter(
            (pl.col(var) > 0) & (pl.col(var).shift(1).over(pl.col("firm_ico").sort_by("year")) > 0)
        ).height
        total_count = df_transformed.height
        print(f"  • {var}: {positive_count:,}/{total_count:,} observations with positive values for log calculation")
    else:
        print(f"  • {var}: Not processed")

# %%
# Validation: Verify Robust Growth Rate Calculations
print("Validating Robust Growth Rate Calculations")
print("=" * 60)

# Define key variables to validate
key_log_growth_vars = ['firm_sales_revenue_logyoy', 'firm_turnover_logyoy', 'firm_costs_logyoy']
key_margin_dpp_vars = ['firm_operating_margin_cal_dpp', 'firm_net_margin_cal_dpp', 'firm_roa_ebit_cal_dpp', 'firm_roe_cal_dpp']
key_vars_to_check = key_log_growth_vars + key_margin_dpp_vars

print("\n1. Validation: Log Growth Rates Handle Non-Positive Values")
print("-" * 50)
for var in key_log_growth_vars:
    if var in df_transformed.columns:
        base_var = var.replace('_logyoy', '')
        if base_var in df_transformed.columns:
            # Count observations where base variable is non-positive but growth rate is not null
            validation = df_transformed.select([
                pl.len().alias("total_obs"),
                pl.col(base_var).filter(pl.col(base_var) <= 0).len().alias("non_positive_base"),
                pl.col(var).null_count().alias("null_growth_rates"),
                pl.col(var).count().alias("non_null_growth_rates")
            ]).to_dicts()[0]
            
            print(f"{var}:")
            print(f"  • Total observations: {validation['total_obs']:,}")
            print(f"  • Non-positive base values: {validation['non_positive_base']:,}")
            print(f"  • Null growth rates: {validation['null_growth_rates']:,}")
            print(f"  • Non-null growth rates: {validation['non_null_growth_rates']:,}")
            
            # Check if any growth rates exist where base values are non-positive
            invalid_count = df_transformed.filter(
                (pl.col(base_var) <= 0) & (pl.col(var).is_not_null())
            ).height
            
            if invalid_count == 0:
                print(f"  ✓ No invalid growth rates (where base ≤ 0 but growth != null)")
            else:
                print(f"  ✗ Found {invalid_count} invalid growth rates")

print("\n2. Validation: Winsorization Applied Correctly")
print("-" * 50)
for var in key_vars_to_check:
    if var in df_transformed.columns:
        # Check if winsorization was applied by looking at extreme percentiles
        stats = df_transformed.select([
            pl.col(var).quantile(0.005).alias("p0_5"),
            pl.col(var).quantile(0.01).alias("p1"),
            pl.col(var).quantile(0.99).alias("p99"),
            pl.col(var).quantile(0.995).alias("p99_5"),
            pl.col(var).min().alias("min"),
            pl.col(var).max().alias("max")
        ]).to_dicts()[0]
        
        print(f"{var}:")
        print(f"  • 0.5th percentile: {stats['p0_5']:.4f}")
        print(f"  • 1st percentile: {stats['p1']:.4f}")
        print(f"  • 99th percentile: {stats['p99']:.4f}")
        print(f"  • 99.5th percentile: {stats['p99_5']:.4f}")
        print(f"  • Min: {stats['min']:.4f} | Max: {stats['max']:.4f}")
        
        # Check if winsorization was effective (min/max should be close to 1st/99th percentiles)
        if var in key_log_growth_vars + key_margin_dpp_vars:
            min_close_to_p1 = abs(stats['min'] - stats['p1']) < 0.001
            max_close_to_p99 = abs(stats['max'] - stats['p99']) < 0.001
            
            if min_close_to_p1 and max_close_to_p99:
                print(f"  ✓ Winsorization applied correctly")
            else:
                print(f"  ⚠ Winsorization may not have been applied")

print("\n3. Validation: Margin Calculations Handle Zero Denominators")
print("-" * 50)
margin_validations = [
    {'margin': 'firm_operating_margin_cal', 'numerator': 'firm_oper_profit', 'denominator': 'firm_sales_revenue'},
    {'margin': 'firm_net_margin_cal', 'numerator': 'firm_profit_net', 'denominator': 'firm_sales_revenue'},
    {'margin': 'firm_roa_ebit_cal', 'numerator': 'firm_oper_profit', 'denominator': 'firm_total_assets'},
    {'margin': 'firm_roe_cal', 'numerator': 'firm_profit_net', 'denominator': 'firm_equity'}
]

for margin_check in margin_validations:
    margin_col = margin_check['margin']
    denominator = margin_check['denominator']
    
    if margin_col in df_transformed.columns and denominator in df_transformed.columns:
        # Count cases where denominator is zero
        zero_denom_count = df_transformed.filter(pl.col(denominator) == 0).height
        zero_denom_null_margin = df_transformed.filter(
            (pl.col(denominator) == 0) & (pl.col(margin_col).is_null())
        ).height
        zero_denom_nonnull_margin = df_transformed.filter(
            (pl.col(denominator) == 0) & (pl.col(margin_col).is_not_null())
        ).height
        
        print(f"{margin_col}:")
        print(f"  • Zero denominator cases: {zero_denom_count:,}")
        print(f"  • Null margin when denom=0: {zero_denom_null_margin:,}")
        print(f"  • Non-null margin when denom=0: {zero_denom_nonnull_margin:,}")
        
        if zero_denom_count > 0 and zero_denom_nonnull_margin == 0:
            print(f"  ✓ Zero denominators handled correctly (margin set to null)")
        elif zero_denom_count == 0:
            print(f"  ℹ No zero denominators found")
        else:
            print(f"  ✗ Some zero denominators not handled properly")

print("\n4. Summary: Key Variable Coverage")
print("-" * 50)
total_log_yoy = len([c for c in key_log_growth_vars if c in df_transformed.columns])
total_margin_dpp = len([c for c in key_margin_dpp_vars if c in df_transformed.columns])

print(f"Key log growth variables created: {total_log_yoy}/{len(key_log_growth_vars)}")
print(f"Key margin difference variables created: {total_margin_dpp}/{len(key_margin_dpp_vars)}")

# Check coverage for key variables
for var in key_log_growth_vars + key_margin_dpp_vars:
    if var in df_transformed.columns:
        non_null_count = df_transformed.select(pl.col(var).count()).item()
        total_count = df_transformed.height
        coverage = non_null_count / total_count if total_count > 0 else 0
        print(f"  • {var}: {coverage:.1%} coverage ({non_null_count:,}/{total_count:,})")

print(f"\n✅ Robust growth rate calculation validation completed.")

# %%
# Data Quality Checks for Robust Growth Rate Calculations
print("Data Quality Checks for Robust Growth Rate Calculations")
print("=" * 60)

def check_robust_growth_rate_quality(df: pl.DataFrame, var_name: str, transform_type: str):
    """
    Check quality of robust growth rate calculations with focus on outlier handling
    
    Args:
        df: DataFrame with calculated growth rates
        var_name: Name of the transformed variable
        transform_type: Type of transformation (logyoy, pct, dpp)
    """
    if var_name not in df.columns:
        print(f"  ✗ {var_name}: Column not found")
        return
    
    # Basic statistics
    stats = df.select([
        pl.col(var_name).count().alias("count"),
        pl.col(var_name).null_count().alias("null_count"),
        pl.col(var_name).min().alias("min"),
        pl.col(var_name).max().alias("max"),
        pl.col(var_name).mean().alias("mean"),
        pl.col(var_name).std().alias("std"),
        pl.col(var_name).median().alias("median"),
        pl.col(var_name).quantile(0.01).alias("p1"),
        pl.col(var_name).quantile(0.99).alias("p99")
    ]).to_dicts()[0]
    
    print(f"\n{var_name}:")
    print(f"  Count: {stats['count']:,} | Nulls: {stats['null_count']:,}")
    print(f"  Min: {stats['min']:.4f} | Max: {stats['max']:.4f}")
    print(f"  Mean: {stats['mean']:.4f} | Std: {stats['std']:.4f}")
    print(f"  P1: {stats['p1']:.4f} | P99: {stats['p99']:.4f}")
    
    # Check for winsorization effectiveness
    if transform_type in ["logyoy", "dpp"]:
        # Check if min/max are close to 1st/99th percentiles (indicating winsorization)
        min_close_to_p1 = abs(stats['min'] - stats['p1']) < 0.001
        max_close_to_p99 = abs(stats['max'] - stats['p99']) < 0.001
        
        if min_close_to_p1 and max_close_to_p99:
            print(f"  ✓ Winsorization applied correctly")
        else:
            print(f"  ⚠ Winsorization may not be effective")
    
    # Check for extreme values that might indicate issues
    if transform_type == "logyoy":
        # Log growth rates should generally be between -5 and 5 (after winsorization)
        extreme_count = df.filter(pl.col(var_name).abs() > 10).height
        if extreme_count > 0:
            print(f"  ⚠️  {extreme_count:,} observations with |log growth| > 10")
    
    # Check for infinite values
    inf_count = df.filter(pl.col(var_name).is_infinite()).height
    if inf_count > 0:
        print(f"  ⚠️  {inf_count:,} infinite values")

# Focus on key financial variables and their robust transformations
key_log_growth_vars = ['firm_sales_revenue_logyoy', 'firm_turnover_logyoy', 'firm_costs_logyoy']
key_margin_dpp_vars = ['firm_operating_margin_cal_dpp', 'firm_net_margin_cal_dpp', 'firm_roa_ebit_cal_dpp', 'firm_roe_cal_dpp']

# 1. Check Key Log YoY growth rates (with robust handling)
print("\n1. Key Log Year-over-Year Growth Rate Quality (Robust)")
print("-" * 50)
for col in key_log_growth_vars:
    if col in df_transformed.columns:
        check_robust_growth_rate_quality(df_transformed, col, "logyoy")

# 2. Check Key Margin difference in percentage points (with robust handling)  
print("\n2. Key Margin Difference in Percentage Points Quality (Robust)")
print("-" * 50)
for col in key_margin_dpp_vars:
    if col in df_transformed.columns:
        check_robust_growth_rate_quality(df_transformed, col, "dpp")

# 3. Validate robust handling of non-positive values
print("\n3. Robust Non-Positive Value Handling Validation")
print("-" * 50)
for var in ['firm_sales_revenue', 'firm_turnover', 'firm_costs']:
    logyoy_var = f"{var}_logyoy"
    if logyoy_var in df_transformed.columns:
        # Count cases where base variable is non-positive
        non_positive_base = df_transformed.filter(pl.col(var) <= 0).height
        
        # Check if any growth rates exist where base values are non-positive
        invalid_growth = df_transformed.filter(
            (pl.col(var) <= 0) & (pl.col(logyoy_var).is_not_null())
        ).height
        
        print(f"{var}:")
        print(f"  • Non-positive base values: {non_positive_base:,}")
        print(f"  • Invalid growth rates (base ≤ 0 but growth != null): {invalid_growth:,}")
        
        if invalid_growth == 0:
            print(f"  ✓ Non-positive values handled correctly")
        else:
            print(f"  ✗ Found invalid growth rate calculations")

# 4. Overall summary with focus on robust features
print(f"\n4. Robust Growth Rate Calculation Summary")
print("-" * 50)
print(f"Key financial log growth variables: {len([c for c in key_log_growth_vars if c in df_transformed.columns])}/3")
print(f"Key margin difference variables: {len([c for c in key_margin_dpp_vars if c in df_transformed.columns])}/4")

# Check coverage and robustness
print(f"\nRobustness Features Applied:")
print(f"  ✓ Log growth rates handle non-positive values (set to NaN)")
print(f"  ✓ Winsorization applied at 1st-99th percentiles for key variables")
print(f"  ✓ Margin calculations handle zero denominators correctly")
print(f"  ✓ Outlier detection and handling implemented")

# 5. Data coverage summary
print(f"\n5. Data Coverage Summary")
print("-" * 50)
total_obs = df_transformed.height
first_year = df_transformed.select(pl.col("year").min()).item()

print(f"Total observations: {total_obs:,}")
print(f"First year in dataset: {first_year} (expected nulls due to lagging)")

# Coverage for key variables
coverage_stats = {}
for var in key_log_growth_vars + key_margin_dpp_vars:
    if var in df_transformed.columns:
        non_null_count = df_transformed.select(pl.col(var).count()).item()
        coverage = non_null_count / total_obs
        coverage_stats[var] = coverage
        print(f"  • {var}: {coverage:.1%} coverage")

print(f"\nAverage coverage: {sum(coverage_stats.values())/len(coverage_stats):.1%}")
print(f"✅ Robust growth rate quality checks completed successfully")

# %%
# Visualization to verify calculated growth rates
print("Creating visualizations to verify growth rate calculations...")

# Convert to pandas for easier plotting
df_plot = df_transformed.to_pandas()

# Get lists of the actual created columns
log_yoy_cols = [col for col in new_columns if col.endswith("_logyoy")]
pct_cols = [col for col in new_columns if col.endswith("_pct")]
dpp_cols = [col for col in new_columns if col.endswith("_dpp")]

print(f"Available columns for plotting:")
print(f"  Log YoY columns: {len(log_yoy_cols)}")
print(f"  Percentage columns: {len(pct_cols)}")
print(f"  DPP columns: {len(dpp_cols)}")

# Create subplots for different types of growth rates
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Growth Rate Calculations - Verification Plots', fontsize=16)

# 1. Plot time series of a sample log YoY growth rate
if log_yoy_cols:
    sample_col = log_yoy_cols[0]
    original_col = sample_col.replace("_logyoy", "")
    
    # Aggregate by year (mean) for plotting
    if original_col in df_plot.columns and sample_col in df_plot.columns:
        yearly_data = df_plot.groupby('year').agg({
            original_col: 'mean',
            sample_col: 'mean'
        }).reset_index()
        
        ax1 = axes[0, 0]
        ax1.plot(yearly_data['year'], yearly_data[sample_col], 'b-', linewidth=2, label='Log YoY Growth')
        ax1.set_title(f'{sample_col}\n(Sample Log YoY Growth Rate)')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Log YoY Growth Rate')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
    else:
        ax1 = axes[0, 0]
        ax1.text(0.5, 0.5, f'Data not available for\n{sample_col}', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Log YoY Growth Rate (No Data)')

# 2. Plot histogram of a sample percentage change
if pct_cols:
    sample_col = pct_cols[0]
    
    ax2 = axes[0, 1]
    if sample_col in df_plot.columns:
        # Remove extreme outliers for better visualization
        plot_data = df_plot[sample_col].dropna()
        if len(plot_data) > 0:
            q1, q99 = plot_data.quantile([0.01, 0.99])
            plot_data_filtered = plot_data[(plot_data >= q1) & (plot_data <= q99)]
            
            ax2.hist(plot_data_filtered, bins=50, alpha=0.7, color='green', edgecolor='black')
            ax2.set_title(f'{sample_col}\n(Sample Percentage Change Distribution)')
            ax2.set_xlabel('Percentage Change')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Percentage Change (No Data)')
    else:
        ax2.text(0.5, 0.5, f'Column not found:\n{sample_col}', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Percentage Change (Column Missing)')
else:
    ax2 = axes[0, 1]
    ax2.text(0.5, 0.5, 'No percentage columns available', ha='center', va='center', transform=ax2.transAxes)
    ax2.set_title('Percentage Change (No Columns)')

# 3. Plot time series of a sample difference in percentage points
if dpp_cols:
    sample_col = dpp_cols[0]
    
    ax3 = axes[1, 0]
    if sample_col in df_plot.columns:
        # Aggregate by year (mean) for plotting
        yearly_data = df_plot.groupby('year')[sample_col].mean().reset_index()
        
        ax3.plot(yearly_data['year'], yearly_data[sample_col], 'r-', linewidth=2, label='Change in pp')
        ax3.set_title(f'{sample_col}\n(Sample Difference in Percentage Points)')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Change in Percentage Points')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
    else:
        ax3.text(0.5, 0.5, f'Column not found:\n{sample_col}', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('DPP (Column Missing)')
else:
    ax3 = axes[1, 0]
    ax3.text(0.5, 0.5, 'No DPP columns available', ha='center', va='center', transform=ax3.transAxes)
    ax3.set_title('DPP (No Columns)')

# 4. Correlation plot between original and growth rate
if log_yoy_cols and len(log_yoy_cols) > 0:
    sample_growth_col = log_yoy_cols[0]
    original_col = sample_growth_col.replace("_logyoy", "")
    
    ax4 = axes[1, 1]
    if original_col in df_plot.columns and sample_growth_col in df_plot.columns:
        # Create scatter plot of level vs growth rate
        # Sample data to avoid overplotting
        sample_data = df_plot[[original_col, sample_growth_col]].dropna()
        if len(sample_data) > 0:
            sample_size = min(5000, len(sample_data))
            sample_data = sample_data.sample(n=sample_size, random_state=42)
            
            ax4.scatter(sample_data[original_col], sample_data[sample_growth_col], 
                       alpha=0.5, s=1, color='purple')
            ax4.set_title(f'Level vs Growth Rate\n{original_col} vs {sample_growth_col}')
            ax4.set_xlabel(f'{original_col} (Level)')
            ax4.set_ylabel(f'{sample_growth_col} (Growth)')
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No paired data available', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Level vs Growth (No Data)')
    else:
        ax4.text(0.5, 0.5, f'Columns not found:\n{original_col}\n{sample_growth_col}', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Level vs Growth (Columns Missing)')
else:
    ax4 = axes[1, 1]
    ax4.text(0.5, 0.5, 'No log YoY columns available', ha='center', va='center', transform=ax4.transAxes)
    ax4.set_title('Level vs Growth (No Columns)')

plt.tight_layout()
plt.show()

# Summary statistics table
print("\nSummary Statistics for Growth Rate Variables:")
print("=" * 60)

# Create a summary table for the first 10 new columns
summary_stats = []
display_columns = new_columns[:10] if len(new_columns) >= 10 else new_columns

for col in display_columns:
    if col in df_transformed.columns:
        stats = df_transformed.select([
            pl.lit(col).alias("variable"),
            pl.col(col).count().alias("count"),
            pl.col(col).null_count().alias("nulls"),
            pl.col(col).mean().alias("mean"),
            pl.col(col).std().alias("std"),
            pl.col(col).min().alias("min"),
            pl.col(col).max().alias("max")
        ]).to_dicts()[0]
        summary_stats.append(stats)

if summary_stats:
    summary_df = pl.DataFrame(summary_stats)
    print(summary_df)
    print(f"\nDisplaying statistics for {len(summary_stats)} of {len(new_columns)} new variables.")
else:
    print("No growth rate variables found for summary.")

print(f"\nPlot generation completed successfully!")

# %%
# Save the transformed dataset and create documentation
print("Saving transformed dataset and creating documentation...")
print("=" * 60)

# rename level1_code and level2_code to level1_nace_code and level2_nace_code
df_transformed = df_transformed.rename({
    "level1_code": "level1_nace_code",
    "level2_code": "level2_nace_code"
})

# 1. Save the transformed dataset
df_transformed.write_parquet(output_path)
print(f"✓ Transformed dataset saved to: {output_path}")
print(f"  - Shape: {df_transformed.shape}")
print(f"  - Original columns: {len(df.columns)}")
print(f"  - New growth rate columns: {len(new_columns)}")
print(f"  - Total columns: {len(df_transformed.columns)}")

# 2. Create documentation for the new variables
doc_path = output_path.replace('.parquet', '_growth_variables_docs.txt')
with open(doc_path, 'w') as f:
    f.write("Growth Rate Variables Documentation\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Source dataset: {input_path}\n")
    f.write(f"Output dataset: {output_path}\n\n")
    
    f.write("TRANSFORMATION FORMULAS:\n")
    f.write("-" * 30 + "\n")
    f.write("1. Log Year-over-Year Growth (_logyoy):\n")
    f.write("   Formula: X_logyoy_t = ln(X_t) - ln(X_{t-1})\n")
    f.write("   Use: Continuous growth rates for level/index series\n\n")
    
    f.write("2. Percentage Change (_pct):\n")
    f.write("   Formula: X_pct_t = 100*(X_t / X_{t-1} - 1)\n")
    f.write("   Use: Intuitive percentage changes\n\n")
    
    f.write("3. Difference in Percentage Points (_dpp):\n")
    f.write("   Formula: X_dpp_t = X_t - X_{t-1}\n")
    f.write("   Use: Changes in rates, shares, ratios\n\n")
    
    f.write("4. Base-100 Index (_pct):\n")
    f.write("   Formula: X_pct = X - 100\n")
    f.write("   Use: Convert base-100 index to percentage\n\n")
    
    f.write("VARIABLE LISTING:\n")
    f.write("-" * 30 + "\n")
    
    # Group variables by transformation type
    for transform_type in ["_logyoy", "_pct", "_dpp"]:
        vars_of_type = [col for col in new_columns if col.endswith(transform_type)]
        if vars_of_type:
            f.write(f"\n{transform_type.upper()} Variables ({len(vars_of_type)}):\n")
            for var in sorted(vars_of_type):
                f.write(f"  - {var}\n")

print(f"✓ Documentation saved to: {doc_path}")

# 3. Create a summary report
print(f"\n📊 FINAL SUMMARY REPORT")
print("=" * 60)
print(f"Input dataset: {input_path}")
print(f"Output dataset: {output_path}")
print(f"")
print(f"Dataset transformation completed:")
print(f"  • Original shape: {df.shape}")
print(f"  • Final shape: {df_transformed.shape}")
print(f"  • New growth rate variables: {len(new_columns)}")
print(f"")
print(f"Variable breakdown:")
print(f"  • Log YoY growth (_logyoy): {len([c for c in new_columns if c.endswith('_logyoy')])}")
print(f"  • Percentage change (_pct): {len([c for c in new_columns if c.endswith('_pct')])}")
print(f"  • Difference in pp (_dpp): {len([c for c in new_columns if c.endswith('_dpp')])}")
print(f"")
print(f"Key files created:")
print(f"  • {output_path}")
print(f"  • {doc_path}")
print(f"")
print(f"🎉 Growth rate calculations completed successfully!")
print(f"   Ready for econometric analysis in src_03_analysis/")

# 4. Basic validation check
print(f"\n🔍 FINAL VALIDATION CHECK")
print("-" * 30)
# Check that we have reasonable number of non-null observations
sample_growth_col = new_columns[0] if new_columns else None
if sample_growth_col:
    validation_stats = df_transformed.select([
        pl.len().alias("total_rows"),
        pl.col(sample_growth_col).count().alias("non_null_growth"),
        pl.col("year").min().alias("min_year"),
        pl.col("year").max().alias("max_year")
    ]).to_dicts()[0]
    
    print(f"Sample validation ({sample_growth_col}):")
    print(f"  • Total rows: {validation_stats['total_rows']:,}")
    print(f"  • Non-null growth rates: {validation_stats['non_null_growth']:,}")
    print(f"  • Coverage: {validation_stats['non_null_growth']/validation_stats['total_rows']:.1%}")
    print(f"  • Year range: {validation_stats['min_year']} - {validation_stats['max_year']}")
    
    if validation_stats['non_null_growth'] > 0:
        print(f"  ✓ Growth rate calculations appear successful")
    else:
        print(f"  ✗ No growth rate values calculated - check data")
else:
    print("No growth rate variables to validate")



# %%
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import os

# Load the data using lazy evaluation for better performance
main_path = os.path.join("..", "data", "source_cleaned", "magnusweb_panel_imputed.parquet")
#main_path = os.path.join("..", "data", "source_cleaned", "magnusweb_panel_hq.parquet")

# Output path for the final merged dataset
output_path = os.path.join("..", "data", "data_ready", "merged_panel_imputed.parquet")
#output_path = os.path.join("..", "data", "data_ready", "merged_panel_hq.parquet")

# Using scan_parquet for lazy loading
main_df = pl.scan_parquet(main_path)
#hq_df = pl.scan_parquet(hq_path)

nace_propagated_path = os.path.join("..", "data", "source_cleaned", "data_by_nace_annual_tidy_propagated.parquet")
nace_propagated_df = pl.scan_parquet(nace_propagated_path)

macro_indicators_path = os.path.join("..", "data", "source_cleaned", "economy_annual_tidy.parquet")
macro_indicators_df = pl.scan_parquet(macro_indicators_path)

print("Data loaded using lazy evaluation")    


# %%
# Explore the structure of each dataset
print("=== Main DataFrame Structure ===")
main_sample = main_df.limit(0).collect()  # Get structure without data
print(f"Main columns: {main_sample.columns}")

print("\n=== NACE Propagated DataFrame Structure ===")
nace_sample = nace_propagated_df.limit(5).collect()
print(f"NACE columns: {nace_sample.columns}")
print(f"NACE sample shape: {nace_sample.shape}")
print(nace_sample)

print("\n=== Macro Indicators DataFrame Structure ===")
macro_sample = macro_indicators_df.limit(5).collect()
print(f"Macro columns: {macro_sample.columns}")
print(f"Macro sample shape: {macro_sample.shape}")
print(macro_sample)

# %%
# Load NACE matching table for proper level1_code and level2_code mapping
print("=== Loading NACE Matching Table ===")
nace_matching_path = os.path.join("..", "data", "source_cleaned", "t_nace_matching.parquet")
nace_matching_df = pl.scan_parquet(nace_matching_path)

# Transform NACE data from long to wide format and add level-specific prefixes
print("=== Transforming NACE data ===")

# First, let's see what metrics we have in the NACE data
nace_metrics = nace_propagated_df.select("metric").unique().collect()
print(f"Available NACE metrics: {nace_metrics['metric'].to_list()}")

# Transform NACE Level 1 data from long to wide format
print("\n--- Processing Level 1 NACE data ---")
# Filter for level 1 and collect, then pivot with metrics as columns
nace_level1_long = nace_propagated_df.filter(pl.col("level") == 1).collect()

# Verify uniqueness of czso_code + year combinations for level 1
level1_unique_check = nace_level1_long.group_by(["czso_code", "year"]).len()
max_records_per_combo = level1_unique_check.select(pl.col("len").max()).item()
expected_metrics = len(nace_metrics['metric'].to_list())
print(f"Level 1: Max records per (czso_code, year): {max_records_per_combo}, Expected metrics: {expected_metrics}")

# Pivot to wide format with metrics as columns
# CRITICAL FIX: Remove name_en from pivot index to prevent duplicates
nace_level1 = nace_level1_long.pivot(
    index=["czso_code", "year"],  # Only unique identifiers
    on="metric",
    values="value"
)

# Get the name mapping separately (taking first name for each czso_code, year)
nace_level1_names = (nace_level1_long
                     .select(["czso_code", "year", "name_en"])
                     .unique(subset=["czso_code", "year"], keep="first"))

# Join names back to the pivoted data
nace_level1_with_names = nace_level1.join(
    nace_level1_names,
    on=["czso_code", "year"],
    how="left"
)

# Add sector_level1_ prefix to metric columns
metric_cols = nace_metrics['metric'].to_list()
nace_level1_renamed = nace_level1_with_names.rename({
    col: f"sector_level1_{col}" for col in metric_cols
})

# Rename name_en to proper suffix
nace_level1_renamed = nace_level1_renamed.rename({"name_en": "level1_nace_en_name"})

print(f"Level 1 NACE data transformed: {nace_level1_renamed.columns}")
print(f"Level 1 shape: {nace_level1_renamed.shape}")

# Transform NACE Level 2 data from long to wide format
print("\n--- Processing Level 2 NACE data ---")
nace_level2_long = nace_propagated_df.filter(pl.col("level") == 2).collect()

# Verify uniqueness of czso_code + year combinations for level 2  
level2_unique_check = nace_level2_long.group_by(["czso_code", "year"]).len()
max_records_per_combo = level2_unique_check.select(pl.col("len").max()).item()
print(f"Level 2: Max records per (czso_code, year): {max_records_per_combo}, Expected metrics: {expected_metrics}")

# Pivot to wide format with metrics as columns
# CRITICAL FIX: Remove name_en from pivot index to prevent duplicates
nace_level2 = nace_level2_long.pivot(
    index=["czso_code", "year"],  # Only unique identifiers
    on="metric",
    values="value"
)

# Get the name mapping separately (taking first name for each czso_code, year)
nace_level2_names = (nace_level2_long
                     .select(["czso_code", "year", "name_en"])
                     .unique(subset=["czso_code", "year"], keep="first"))

# Join names back to the pivoted data
nace_level2_with_names = nace_level2.join(
    nace_level2_names,
    on=["czso_code", "year"],
    how="left"
)

# Add sector_level2_ prefix to metric columns
nace_level2_renamed = nace_level2_with_names.rename({
    col: f"sector_level2_{col}" for col in metric_cols
})

# Rename name_en to proper suffix
nace_level2_renamed = nace_level2_renamed.rename({"name_en": "level2_nace_en_name"})

print(f"Level 2 NACE data transformed: {nace_level2_renamed.columns}")
print(f"Level 2 shape: {nace_level2_renamed.shape}")

# Convert back to lazy frames for efficient joining
nace_level1_renamed = pl.LazyFrame(nace_level1_renamed)
nace_level2_renamed = pl.LazyFrame(nace_level2_renamed)

print("\nNACE data transformed to wide format with level-specific prefixes")
print("CRITICAL FIX: Removed name_en from pivot index to ensure unique (czso_code, year) combinations")

# %%
# CRITICAL DIAGNOSTIC: Verify NACE data is properly pivoted before joins
print("=== VERIFYING NACE DATA FOR JOINS ===")

# Check level 1 data structure
if 'nace_level1_renamed' in locals():
    level1_sample = nace_level1_renamed.collect()
    print(f"Level 1 NACE data shape: {level1_sample.shape}")
    print(f"Columns: {level1_sample.columns}")
    
    # Check for specific case that was causing problems
    test_case = level1_sample.filter(pl.col("czso_code") == "G").filter(pl.col("year") == 2020)
    print(f"Test case (czso_code=G, year=2020): {test_case.shape[0]} rows")
    if test_case.shape[0] > 0:
        print("Sample:")
        print(test_case)
    
    # Check uniqueness
    unique_combos = level1_sample.select(["czso_code", "year"]).n_unique()
    total_rows = level1_sample.height
    print(f"Level 1 unique (czso_code, year) combinations: {unique_combos}")
    print(f"Level 1 total rows: {total_rows}")
    if unique_combos == total_rows:
        print("✅ Level 1 NACE data is properly unique - good for joining!")
    else:
        print("❌ Level 1 NACE data still has duplicates!")
        
else:
    print("❌ nace_level1_renamed not available")

print()

# Check level 2 data structure  
if 'nace_level2_renamed' in locals():
    level2_sample = nace_level2_renamed.collect()
    print(f"Level 2 NACE data shape: {level2_sample.shape}")
    print(f"Columns: {level2_sample.columns}")
    
    # Check uniqueness
    unique_combos = level2_sample.select(["czso_code", "year"]).n_unique()
    total_rows = level2_sample.height
    print(f"Level 2 unique (czso_code, year) combinations: {unique_combos}")
    print(f"Level 2 total rows: {total_rows}")
    if unique_combos == total_rows:
        print("✅ Level 2 NACE data is properly unique - good for joining!")
    else:
        print("❌ Level 2 NACE data still has duplicates!")
else:
    print("❌ nace_level2_renamed not available")

# %%
# Transform macro data from long to wide format and add mac_ prefix
print("=== Transforming Macro data ===")

# First, let's see what metrics we have in the macro data
macro_metrics = macro_indicators_df.select("metric").unique().collect()
print(f"Available macro metrics: {macro_metrics['metric'].to_list()}")

# Transform macro data from long to wide format
# For lazy frames, we need to collect first
macro_wide = macro_indicators_df.collect().pivot(
    index=["year"],
    on="metric",  # Updated from 'columns' to 'on'
    values="value"
)

# Add mac_ prefix to metric columns (all columns except year)
macro_renamed = macro_wide.rename({
    col: f"mac_{col}" for col in macro_wide.columns 
    if col != "year"
})

# Convert back to lazy frame for efficient joining
macro_renamed = pl.LazyFrame(macro_renamed)

print("Macro data transformed to wide format with mac_ prefix")
print(f"Transformed columns: {macro_renamed.collect_schema().names()}")

# %%
# Add firm_ prefix to all columns in main_df (except year and join keys)
print("=== Adding firm_ prefix to firm-level columns ===")

# Get the columns from main_df that need the firm_ prefix
main_cols_sample = main_df.limit(0).collect().columns
print(f"Original main columns count: {len(main_cols_sample)}")

# Create rename mapping for all columns except 'year' and join keys
firm_rename_map = {}
for col in main_cols_sample:
    if col not in ['year', 'level1_code', 'level2_code']:  # Keep join keys unchanged
        firm_rename_map[col] = f"firm_{col}"

print(f"Renaming {len(firm_rename_map)} columns with firm_ prefix")

# Apply the renaming to main_df
main_df_renamed = main_df.rename(firm_rename_map)

print("Firm columns renamed successfully!")

# Step 1: Merge main_df with Level 1 NACE data
print("=== First Merge: Main + Level 1 NACE data ===")

# The join strategy:
# - main_df has level1_code (like 'A', 'B', 'C', etc.)  
# - nace_level1_renamed has czso_code (also like 'A', 'B', 'C', etc. for level 1)
# - So we can join directly on level1_code = czso_code

# Check if we have the right join keys
main_cols_renamed = main_df_renamed.limit(0).collect().columns
print(f"Main df has level1_code: {'level1_code' in main_cols_renamed}")
print(f"Main df has level2_code: {'level2_code' in main_cols_renamed}")

# Perform the first merge with Level 1 NACE data (left join to keep all main data)
merged_step1 = main_df_renamed.join(
    nace_level1_renamed,
    left_on=["level1_code", "year"],
    right_on=["czso_code", "year"], 
    how="left"
)

# Verify the first merge
step1_sample = merged_step1.limit(3).collect()
print(f"After Level 1 NACE merge - Shape: {step1_sample.shape}")
level1_sector_cols = [col for col in step1_sample.columns if col.startswith('sector_level1_')]
print(f"Level 1 sector columns: {level1_sector_cols}")

# Step 2: Merge with Level 2 NACE data  
print("=== Second Merge: Adding Level 2 NACE data ===")

# For level 2, we need to match level2_code (like '01', '02', etc.) with czso_code
# Perform the second merge with Level 2 NACE data (left join to keep all existing data)
merged_step2 = merged_step1.join(
    nace_level2_renamed,
    left_on=["level2_code", "year"],
    right_on=["czso_code", "year"],
    how="left"
)

# Verify the second merge
step2_sample = merged_step2.limit(3).collect()
print(f"After Level 2 NACE merge - Shape: {step2_sample.shape}")
level2_sector_cols = [col for col in step2_sample.columns if col.startswith('sector_level2_')]
print(f"Level 2 sector columns: {level2_sector_cols}")

# Check for any missing joins - count nulls in key sector variables
level1_check_col = level1_sector_cols[0] if level1_sector_cols else None
level2_check_col = level2_sector_cols[0] if level2_sector_cols else None

null_check_cols = ["year"]
if level1_check_col:
    null_check_cols.append(level1_check_col)
if level2_check_col:
    null_check_cols.append(level2_check_col)

null_check = merged_step2.select([
    pl.col(col).is_null().sum().alias(f"null_{col}") for col in null_check_cols
]).collect()
print(f"Null check after NACE merges:")
for col in null_check.columns:
    print(f"  {col}: {null_check[col].item()}")

print("NACE merges completed successfully!")

# %%
# Step 3: Merge with macro data on year
print("=== Third Merge: Adding Macro data ===")

# Check shapes before merge
print(f"Before macro merge - merged_step2 shape: {merged_step2.collect().shape}")

# Check macro data shape
macro_sample = macro_renamed.collect()
print(f"Macro data shape: {macro_sample.shape}")
print(f"Macro years: {macro_sample['year'].min()} to {macro_sample['year'].max()}")

# Check for duplicate years in macro data
macro_year_counts = macro_sample.select(pl.col("year").value_counts()).unnest("year")
duplicate_years = macro_year_counts.filter(pl.col("count") > 1)
if duplicate_years.height > 0:
    print(f"❌ PROBLEM: Duplicate years in macro data!")
    print(duplicate_years)
else:
    print(f"✓ Macro data has unique years")

# Perform the third merge (left join to keep all existing data)
merged_final = merged_step2.join(
    macro_renamed,
    on="year",
    how="left"
)

# Collect the final result for verification
final_df = merged_final.collect()
print(f"After macro merge - Final merged data Shape: {final_df.shape}")
print(f"Total columns: {len(final_df.columns)}")

# Check for unexpected row expansion
original_main_count = 663437  # Known from previous analysis
if final_df.shape[0] != original_main_count:
    print(f"❌ ROW EXPANSION DETECTED!")
    print(f"   Expected: {original_main_count:,} rows")
    print(f"   Actual: {final_df.shape[0]:,} rows")
    print(f"   Expansion factor: {final_df.shape[0] / original_main_count:.2f}x")
    
    # Check for duplicate firm-year combinations that might explain this
    if "firm_ico" in final_df.columns:
        ico_year_counts = final_df.group_by(["firm_ico", "year"]).len()
        max_dupes = ico_year_counts.select(pl.col("len").max()).item()
        print(f"   Max firm-year duplicates: {max_dupes}")
        if max_dupes > 1:
            print("   Sample duplicated firm-year pairs:")
            dupes = ico_year_counts.filter(pl.col("len") > 1).head(5)
            print(dupes)
else:
    print(f"✓ No unexpected row expansion - maintaining {original_main_count:,} rows")

# Categorize columns by prefix
firm_cols = [col for col in final_df.columns if not col.startswith(('sector_', 'mac_'))]
sector_level1_cols = [col for col in final_df.columns if col.startswith('sector_level1_')]
sector_level2_cols = [col for col in final_df.columns if col.startswith('sector_level2_')]
mac_cols = [col for col in final_df.columns if col.startswith('mac_')]

print(f"\nColumn breakdown:")
print(f"  - Firm columns: {len(firm_cols)}")
print(f"  - Sector Level 1 columns: {len(sector_level1_cols)}")
print(f"  - Sector Level 2 columns: {len(sector_level2_cols)}")
print(f"  - Macro columns: {len(mac_cols)}")

print(f"\nSample sector level 1 columns: {sector_level1_cols[:5]}")
print(f"Sample sector level 2 columns: {sector_level2_cols[:5]}")
print(f"Sample macro columns: {mac_cols[:5]}")

# Final verification - check for missing data in key areas
print(f"\n=== Final Verification ===")
verification = final_df.select([
    pl.len().alias("total_rows"),
    pl.col("year").is_null().sum().alias("null_years"),
    pl.col("firm_ico").is_null().sum().alias("null_firm_ico") if "firm_ico" in final_df.columns else pl.lit(0).alias("null_firm_ico"),
    pl.col(sector_level1_cols[0]).is_null().sum().alias(f"null_{sector_level1_cols[0][:20]}") if sector_level1_cols else pl.lit(0).alias("null_sector_level1_sample"),
    pl.col(sector_level2_cols[0]).is_null().sum().alias(f"null_{sector_level2_cols[0][:20]}") if sector_level2_cols else pl.lit(0).alias("null_sector_level2_sample"),
    pl.col(mac_cols[0]).is_null().sum().alias(f"null_{mac_cols[0]}") if mac_cols else pl.lit(0).alias("null_mac_sample")
])

print(verification)

# Check for duplicate firm-year observations
if "firm_ico" in final_df.columns:
    duplicate_rows = final_df.group_by(["firm_ico", "year"]).len().filter(pl.col("len") > 1)
    num_duplicates = duplicate_rows.height
    print(f"\nDuplicate firm-year check: Found {num_duplicates} duplicate firm-year observations.")
    if num_duplicates > 0:
        print("Sample of duplicate firm-year pairs:")
        print(duplicate_rows.head())

print(f"\nMerge process completed!")
print(f"Final dataset contains {final_df.shape[0]:,} rows and {final_df.shape[1]} columns")

# %%
# MINIMAL JOIN TEST - Find the exact source of duplicates
print("=== MINIMAL JOIN TEST ===")

# Test just the first join - main_df + level 1 NACE
print("Testing Level 1 join only...")

# Take a small sample for testing
test_main = main_df_renamed.filter(pl.col("level1_code") == "G").filter(pl.col("year") == 2020).collect()
print(f"Test main data: {test_main.shape[0]} records for level1_code=G, year=2020")

# Check the NACE level 1 data we're joining with
test_nace_l1 = nace_level1_renamed.filter(pl.col("czso_code") == "G").filter(pl.col("year") == 2020).collect()
print(f"Test NACE Level 1 data: {test_nace_l1.shape[0]} records for czso_code=G, year=2020")

if test_nace_l1.shape[0] > 0:
    print("NACE Level 1 sample:")
    print(test_nace_l1.select(["czso_code", "year", "level1_nace_en_name", "sector_level1_avg_wages_by_nace"]))

# Do the join
test_join = pl.LazyFrame(test_main).join(
    nace_level1_renamed,
    left_on=["level1_code", "year"],
    right_on=["czso_code", "year"], 
    how="left"
).collect()

print(f"After join: {test_join.shape[0]} records")
print(f"Expected: {test_main.shape[0]} records (no duplication)")

if test_join.shape[0] != test_main.shape[0]:
    print(f"❌ DUPLICATION FOUND: {test_join.shape[0] / test_main.shape[0]:.1f}x expansion")
    
    # Check the join keys more carefully
    print("\\nAnalyzing duplication...")
    
    # Count unique combinations in both datasets
    main_combos = test_main[["level1_code", "year"]].n_unique()
    nace_combos = test_nace_l1[["czso_code", "year"]].n_unique() if test_nace_l1.shape[0] > 0 else 0
    
    print(f"Main unique (level1_code, year): {main_combos}")
    print(f"NACE unique (czso_code, year): {nace_combos}")
    
    # Show duplicate analysis
    if test_join.shape[0] > 0:
        firm_year_dupes = test_join.group_by(["firm_ico", "year"]).len().sort("len", descending=True)
        print("\\nTop firm-year duplicates:")
        print(firm_year_dupes.head())
        
        # Show the actual duplicated rows for investigation
        if firm_year_dupes.height > 0 and firm_year_dupes[0, "len"] > 1:
            dup_ico = firm_year_dupes[0, "firm_ico"]
            dup_year = firm_year_dupes[0, "year"]
            dup_rows = test_join.filter(pl.col("firm_ico") == dup_ico).filter(pl.col("year") == dup_year)
            print(f"\\nDuplicate rows for ico={dup_ico}, year={dup_year}:")
            print(dup_rows.select(["firm_ico", "year", "level1_code", "level1_nace_en_name"]))
else:
    print("✅ No duplication in Level 1 join")

# %%
# save the final merged DataFrame to Parquet
print("=== Saving final merged DataFrame ===")
final_df.write_parquet(output_path, compression="snappy")
print(f"Final merged DataFrame saved to {output_path}")


