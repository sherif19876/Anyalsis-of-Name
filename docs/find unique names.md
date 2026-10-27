# Unique Name Finder

This script compares two CSV files containing names (one row per name, first column only) and outputs the names from the unclassified file that do not appear in the classified (reference) file. Names are cleaned by lowercasing, stripping whitespace, and normalizing multiple spaces to ensure accurate matching regardless of formatting differences.

## Key features

- Reads only the first column of each CSV (assumed to be the name column).
- Cleans names for reliable comparison (case-insensitive, space-normalized).
- Uses set operations for fast difference calculation.
- Preserves the original (uncleaned) spelling of unique names in the output.
- Removes duplicate names from the output automatically.

## Use case

Ideal for finding new or unregistered names in a voter list, membership roster, or survey response file when compared against an existing master list. For example, identifying which names in an "unknown" file have never been classified before.

## Requirements

- Python 3.6+
- `pandas`
