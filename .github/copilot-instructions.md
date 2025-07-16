## Copilot Instructions for *profit-margins‑inflation*

> Guiding principle: **academic‑grade clarity, reproducibility, and econometric rigor**.  When rules appear to overlap, follow the stricter requirement.

---

Consult: 
- `/specs/specifications.md` for project objectives, data inventory, and analysis modules.  Keep your code in sync with these specifications.
- `/specs/project_status.md` for the latest project status and component progress.
- `/specs/project_objective.md` for the research aim and goals.
- `/specs/data_inventory.json` for the variable inventory in the merged panel dataset.

### 1  General Style & Security

* **No emojis** in any context.
* Write all markdown cells and code comments at a **PhD‑level academic standard**.
* **No global variables** – pass data explicitly via function arguments and returns.
* **Never hard‑code secrets**; surface them through environment variables.
* **Define constants** (avoid “magic numbers”) at the top of notebooks or scripts.

---

### 2  Notebook Workflow

* **Segregate narrative and computation**

  * Do **not** write conclusions in code blocks or `print` statements.
  * Place conclusions **after** cell execution, preferably in the closing markdown cell.
* **Display, don’t persist, intermediates**

  * Charts/tables may be *shown* but are **not saved** to disk.

---

### 3  Data Handling & Preparation

* **Primary engine**: **Polars** in *lazy* mode.

  * Perform *all* transforms lazily; call `.collect()` only for the final tidy DataFrame.
  * Expected columns after collect: `ico`, `year`, *regressors*, *targets*.
  * If memory pressure rises, down‑cast floating columns to `Float32` *before* collect.
* **Data source**: `../data/data_ready/merged_panel_clean.parquet`, with prefixes:

  * `firm_…` – firm‑level variables
  * `sector_…` – NACE level‑2 variables
  * `mac_…` – macro indicators
* **Merges & integrity checks**

  * Count and log duplicate keys **before** merges.
  * Verify row counts and key uniqueness **after** merges.
* **Categorical encodings**

  * Encode categorical predictors with *explicit* category order (alphabetical).
  * Store mapping tables in `/specs/categorical_maps.json`.

---

### 4  Econometric Modeling

* **Panel regressions**: use `linearmodels`.

  * Always write **explicit model specification strings** (e.g., `targets ~ 1 + regressors + EntityEffects + TimeEffects`).
  * Default covariance estimator: `cov_type="clustered"` with **two‑way clustering** (`firm_id`, `year`).
* **Diagnostics & robustness**

  * Report sample size (`n_obs`), number of entities, and R² variants.
  * Log tests for heteroskedasticity, serial correlation, and cross‑sectional dependence in `/diagnostics/`.
  * Use `statsmodels` **only** for diagnostics not handled efficiently by Polars or linearmodels.
* **Iterate until valid**

  * If residual diagnostics fail, refine model specification; do **not** accept invalid results.

---

### 5  Visualization & Reporting

* Use **pandas / numpy** for light wrangling; **matplotlib** or **plotly** for visuals.
* Every figure must include:

  * Labeled axes with units.
  * Descriptive, academic‑quality title.
  * **Alt‑text** supplied in the markdown cell immediately following the figure (`<alt>…</alt>`).
* Follow journal‑quality typography and color‑blind safe palettes.

---

### 6  Dependencies & Project Specs

* **Do not introduce new dependencies** without:

  * Documenting them in `requirements.txt` *and* the first notebook cell.
  * Verifying compatibility with existing versions using `pip‑compile` or `poetry lock --no-update`.
* **Consult project specs**

  * `/specs/` folder for objectives and data inventory (see `/specs/data_inventory.json`).
  * Keep analysis reproducible and in‑sync with specification updates.

---

### 7  Quality Checklist (Pre‑commit)

| Check                              | Pass Criteria                                                           |
| ---------------------------------- | ----------------------------------------------------------------------- |
| **Notebook runs top‑to‑bottom**    | No execution errors; kernel restart‑run passes.                         |
| **`nbQA`**\*\* lint\*\* (optional) | No violations of notebook lint rules (PEP8, conclusions‑in‑code, etc.). |
|                                    |                                                                         |
| **Figures comply with Section 5**  | Axes labels, units, alt‑text present.                                   |

---

### 8  When in Doubt…

Prioritize **clarity**, **reproducibility**, and **academic rigor** over brevity or cleverness.  Document assumptions, justify modeling choices, and iterate until both code and statistical results withstand peer review.
