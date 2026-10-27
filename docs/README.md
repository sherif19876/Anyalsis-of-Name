# Voter Name Analysis Toolkit

A collection of Python tools for matching voter-registration records against
curated name lists and analyzing the geographic distribution of matched
groups by precinct and city council district.

The toolkit is built around a **shared library** (`src/voter_analysis/`) and
**six numbered command-line scripts** (`scripts/`). Each script is a thin
wrapper around the library, so the matching logic is defined in exactly one
place and behaves identically everywhere.

---

## ⚠️ Privacy notice

These scripts process voter files that contain personally identifiable
information (names, addresses, birthdates, party, race). **Never commit raw
data to this repository.** Keep inputs in `data/raw/` and outputs in
`data/output/` — both are `.gitignore`d. Verify your jurisdiction's rules on
voter-file use before running this on production data.

---

## Repository layout

```
voter-name-analysis/
├── README.md                     ← this file
├── pyproject.toml                ← packaging + dependencies
├── requirements.txt              ← pandas, openpyxl
├── .gitignore                    ← excludes data/raw, data/output, *.csv, *.xlsx
├── config/
│   └── config.example.yaml       ← optional; copy to config.yaml
├── data/
│   ├── raw/                      ← PUT YOUR INPUT FILES HERE (gitignored)
│   └── output/                   ← generated files land here (gitignored)
├── docs/                         ← one doc per script, in detail
├── scripts/                      ← the six CLI entry points
│   ├── 01_dedupe_names.py
│   ├── 02_find_unique_names.py
│   ├── 03_match_voter_files.py
│   ├── 04_extract_target_voters.py
│   ├── 05_analyze_by_category.py
│   └── 06_analyze_single_category.py
├── src/voter_analysis/           ← shared library
│   ├── cleaning.py               ← clean_name, normalize_name, clean_precinct
│   ├── io.py                     ← load_voter_file, load_target_names, …
│   ├── matching.py               ← build_category_name_lists, is_in_category
│   └── aggregation.py            ← aggregate_by_district, extract_matched_rows
└── tests/                        ← pytest suite
```

---

## Install

Requires **Python 3.9+**.

```bash
git clone https://github.com/<your-username>/voter-name-analysis.git
cd voter-name-analysis

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e .                   # installs the voter_analysis library
pip install -e ".[dev]"            # add pytest if you want to run tests
```

Verify the install:

```bash
python -c "import voter_analysis; print('ok')"
pytest -q
```

Every script below assumes you are in the repo root with the virtualenv
activated, and that your input files are in `data/raw/`.

---

## Input file formats (reference)

All scripts expect **CSV** or **Excel** files in one of these shapes. Column
names are case-sensitive.

### A. Voter file (`Vlist.csv`, `voter_data.csv`, `FLA_*.xlsx`, etc.)

Must contain at least:

| Column | Example | Notes |
|---|---|---|
| `Precinct` | `304` or `304.1` | Trailing `.1` is stripped automatically |
| `Name First` | `Mohammed` | |
| `Name Last` | `Ali` | |
| `Voter ID` | `123456789` | Used for counting |

Script 04 additionally exports a fixed list of columns (address, party, race,
etc.) if present in your file — missing columns are skipped gracefully.

### B. Target name list (`target_names.csv`)

```csv
First Name,Last Name
Mohammed,Ali
Fatima,Hassan
```

Used by scripts 04 and 06.

### C. Reference name list (`Names_Split.csv`)

```csv
First,Last
Mohammed,Ali
Fatima,Hassan
```

Used by script 03. Note the **shorter** column names (`First`, `Last`, not
`First Name`, `Last Name`).

### D. Name-category map (`all_name_categories.csv`)

```csv
First Name,Last Name,Category
Mohammed,Ali,East African (Muslim)
Fatima,Hassan,East African (Muslim)
Aisha,Okafor,West African (Christian)
Priya,Sharma,South Asian (Hindu)
```

One row per (name, category) pair. A person with two categories gets two rows.
Used by script 05.

### E. Precinct-to-district map (`precincts_city_council_districts.csv`)

```csv
Precinct,City_Council_District
101,1
102,1
201,2
```

Used by scripts 04, 05, and 06.

---

## The six scripts — inputs, command, output

Each section below shows exactly what the script needs and how to run it.

---

### `01_dedupe_names.py` — remove duplicate names

**Purpose:** Given an Excel file where a single column holds names, report
duplicates and keep only the first occurrence of each.

**Inputs**

| File | Required | Format |
|---|---|---|
| Any `.xlsx` with a name column | yes | Excel |

**Run**

```bash
python scripts/01_dedupe_names.py \
    --in  data/raw/Book1.xlsx \
    --out data/output/names_deduplicated.xlsx \
    --column Name
```

**Output:** `names_deduplicated.xlsx` — same columns, duplicates dropped.

---

### `02_find_unique_names.py` — find names not yet classified

**Purpose:** Diff two single-column CSVs. Output every name in the
*unclassified* file that is not already present in the *classified* file.

**Inputs**

| File | Required | Format |
|---|---|---|
| Classified names | yes | CSV, name in column 1 |
| Unclassified names | yes | CSV, name in column 1 |

**Run**

```bash
python scripts/02_find_unique_names.py \
    --classified   data/raw/known_names.csv \
    --unclassified data/raw/unknown_names.csv \
    --out          data/output/missing_names.csv
```

**Output:** `missing_names.csv` — unique names, original spelling preserved.

---

### `03_match_voter_files.py` — match against a reference CSV across multiple voter files

**Purpose:** Clean voter names and reference names, build a `first_last`
composite key, and export the matched rows from each voter file. Also writes
which reference names were **not** found in each file.

**Inputs**

| File | Required | Format |
|---|---|---|
| Reference name list | yes | CSV with `First`, `Last` |
| One or more voter files | yes | Excel, fixed layout (see below) |

**Fixed layout expected in voter Excel files** (overridable with flags):

| Column position | Contains |
|---|---|
| 3rd (index 2) | Last name |
| 5th (index 4) | First name |

If your files have headers, add `--has-header`.

**Run**

```bash
python scripts/03_match_voter_files.py \
    --names data/raw/Names_Split_into_First_and_Last.csv \
    --voter-files data/raw/FLA_20250909.xlsx \
                  data/raw/STJ_20250909.xlsx \
                  data/raw/VOL_20250909.xlsx \
                  data/raw/LAK_20250909.xlsx \
                  data/raw/PUT_20250909.xlsx \
    --out-prefix Namesfin
```

Override column positions if your files differ:

```bash
python scripts/03_match_voter_files.py \
    --names data/raw/Names_Split.csv \
    --voter-files data/raw/my_voters.xlsx \
    --first-col 0 --last-col 1 --has-header \
    --out-prefix Matched
```

**Outputs (per voter file `<name>.xlsx`)**

- `Namesfin_<name>.xlsx` — matched rows
- `Namesfin_<name>_NotFound.xlsx` — reference names not found

---

### `04_extract_target_voters.py` — export full voter rows for a target group

**Purpose:** Take a target name list and a full voter file, return every
voter whose first or last name matches, and (optionally) join in the
precinct-to-district mapping. The output keeps only a curated set of columns
(address, party, race, districts, etc.) so the file is usable for outreach.

**Inputs**

| File | Required | Format |
|---|---|---|
| Voter file | yes | CSV, UTF-8 (BOM ok) |
| Target names | yes | CSV with `First Name`, `Last Name` |
| Precinct-to-district map | optional | CSV with `Precinct`, `City_Council_District` |

**Run**

```bash
python scripts/04_extract_target_voters.py \
    --voter    data/raw/voter_data.csv \
    --names    data/raw/target_names.csv \
    --districts data/raw/precincts_city_council_districts.csv \
    --out      data/output/target_group_voters_filtered.csv
```

Drop `--districts` if you have no mapping file.

**Output:** `target_group_voters_filtered.csv` — matched voter rows with the
curated column set.

---

### `05_analyze_by_category.py` — **canonical analysis**, any number of categories

**Purpose:** Produce district-level counts and percentages for **every**
category in a single name-category CSV. This is the recommended script for
any new analysis, including single-category ones.

**Matching rule:** a voter counts toward a category if their **first name OR
last name** appears in **that category's first-name OR last-name set**. This
is intentionally loose (catches "Mohammed Ali" against a list that only has
"Mohammed") but will over-count very common names. Tune in
`src/voter_analysis/matching.py::is_in_category` if needed.

**Inputs**

| File | Required | Format |
|---|---|---|
| Voter file | yes | CSV with `Precinct`, `Name First`, `Name Last`, `Voter ID` |
| Precinct-to-district map | yes | CSV with `Precinct`, `City_Council_District` |
| Name-category map | yes | CSV with `First Name`, `Last Name`, `Category` |

**Run**

```bash
python scripts/05_analyze_by_category.py \
    --voter      data/raw/Vlist.csv \
    --districts  data/raw/precincts_city_council_districts.csv \
    --categories data/raw/all_name_categories.csv \
    --out        data/output/voter_analysis_by_district_and_category.csv
```

Use non-default column names if needed:

```bash
python scripts/05_analyze_by_category.py \
    --voter data/raw/Vlist.csv \
    --districts data/raw/precincts.csv \
    --categories data/raw/categories.csv \
    --district-col Council_District \
    --id-col VoterID \
    --out data/output/analysis.csv
```

**Output:** `voter_analysis_by_district_and_category.csv` with columns:

```
City_Council_District, Total_Voters,
<Category>_Count, <Category>_Percentage,   (repeated per category)
```

Percentages are rounded to two decimals; districts with zero category
members show `0`.

---

### `06_analyze_single_category.py` — **deprecated**, single-category wrapper

**Purpose:** Historical single-category variant of script 05. Kept so older
command lines reproduce their output. **New work should use 05.**

**Inputs**

| File | Required | Format |
|---|---|---|
| Voter file | yes | CSV with `Precinct`, `Name First`, `Name Last`, `Voter ID` |
| Precinct-to-district map | yes | CSV with `Precinct`, `City_Council_District` |
| Names file | yes | CSV with `First Name`, `Last Name` |

**Run**

```bash
python scripts/06_analyze_single_category.py \
    --voter     data/raw/Vlist.csv \
    --districts data/raw/precincts_city_council_districts.csv \
    --names     "data/raw/Names list WArabchristians.csv" \
    --label     "Central African" \
    --out       data/output/central_african_voters_by_district.csv
```

Note the default encoding for `--names` is `cp1252` (matching the original
script). Pass `--encoding utf-8` if your file is UTF-8.

**Output:** `central_african_voters_by_district.csv` with columns
`City_Council_District`, `Total_Voters`, `Central_African_Voters`,
`Percentage_Central_African_Voters`.

---

## Recommended end-to-end workflow

1. **Deduplicate your curated name list** → script 01
2. **Find any names in the voter file that aren't yet classified** → script 02
3. **Optionally, match against a reference set across many voter files** → script 03
4. **Extract full voter rows for the matched group** (for outreach) → script 04
5. **Aggregate counts and percentages by district** → script 05

Step 04 and step 05 are independent. Run 04 when you need a *person-level*
file; run 05 when you need *district totals*. Many projects run both.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'voter_analysis'`**
You skipped `pip install -e .`. Run it from the repo root.

**`KeyError: 'Precinct'`**
Your voter file uses a different column name. Rename it in the CSV header,
or use script 05's `--district-col` only for the district column (Precinct
must be named `Precinct` exactly for the merge to work).

**Trailing `.1` still present in precincts**
The cleaner strips a single `.1` suffix. Files with `.2`, `.3` will keep the
suffix — adjust `src/voter_analysis/cleaning.py::clean_precinct` if needed.

**Unicode / encoding errors**
- Voter CSVs from Florida-style exports: keep default `utf-8-sig`.
- Curated name lists: often `cp1252`; pass `--encoding cp1252` where supported.

**Fewer matches than expected**
The matching rule is *loose* by design but is exact-string. It won't catch
nicknames ("Bob" vs "Robert") or transliterations ("Mohamed" vs "Mohammed").
Add variants as separate rows in the name list.

**Too many matches**
Common surnames ("Ali", "Mohamed") will match aggressively. For higher
precision, edit `is_in_category` in `src/voter_analysis/matching.py` to
require **both** first and last to match.

---

## Tests

```bash
pytest -q
```

The suite currently covers `clean_name`, `normalize_name`,
`clean_precinct`, and the `is_in_category` matching rule.

---

## License

MIT
