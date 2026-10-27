# Voter File Matcher — Clean, Compare, Match Against a Name List

This script automates the matching of names from multiple voter registration Excel files (e.g., FLA, STJ, VOL, LAK, PUT) against a reference CSV list containing First and Last names. It cleans all names by removing spaces, punctuation, digits, and lowercasing them, then creates a composite key (`first_last`) for exact matching.

## Key features

- Reads voter Excel files with a fixed layout (last name in column 3, first name in column 5 by default).
- Cleans both voter names and reference names using the same aggressive cleaning logic.
- Builds a `first_last` composite key for exact matching.
- Exports matched rows (preserving original formatting) and a list of reference names that were not found in each voter file.
- Reports match counts and misses per file.

## Use case

Ideal for campaigns and community organizations that maintain a curated list of names (e.g., a specific diaspora community) and need to locate those individuals across one or more county voter rolls.

## Requirements

- Python 3.6+
- `pandas`, `openpyxl`

## Inputs

- Reference CSV with columns `First` and `Last`.
- One or more voter Excel files in FLA-style layout.

## Outputs

For each voter file `<name>.xlsx`:
- `<prefix>_<name>.xlsx` — matched rows
- `<prefix>_<name>_NotFound.xlsx` — reference names not found
