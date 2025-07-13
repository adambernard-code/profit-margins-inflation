
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
