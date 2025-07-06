
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

