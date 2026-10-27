"""Single-category variant of 05 — kept for reproducing historical runs.

Deprecated in favour of `05_analyze_by_category.py`, which handles one
category just as well (just pass a single-category CSV). This wrapper
exists so older command lines keep working.

Usage:
    python scripts/06_analyze_single_category.py \
        --voter data/raw/Vlist.csv \
        --districts data/raw/precincts_city_council_districts.csv \
        --names "data/raw/Names list WArabchristians.csv" \
        --label "Central African" \
        --out data/output/central_african_voters_by_district.csv
"""
import argparse
import pandas as pd

from voter_analysis.io import load_voter_file, load_districts
from voter_analysis.matching import is_in_category
from voter_analysis.aggregation import aggregate_by_district


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--voter", required=True)
    p.add_argument("--districts", required=True)
    p.add_argument("--names", required=True,
                   help="CSV with 'First Name' and 'Last Name' columns")
    p.add_argument("--label", default="Central African")
    p.add_argument("--out", dest="output",
                   default="single_category_by_district.csv")
    p.add_argument("--encoding", default="cp1252")
    args = p.parse_args()

    voters = load_voter_file(args.voter)
    districts = load_districts(args.districts)
    names_df = pd.read_csv(args.names, encoding=args.encoding)

    lookup = {
        args.label: {
            "first_names": set(names_df["First Name"].dropna().astype(str).str.strip()),
            "last_names": set(names_df["Last Name"].dropna().astype(str).str.strip()),
        }
    }

    result = aggregate_by_district(voters, districts, lookup)
    # Rename columns to match the historical output format
    result = result.rename(columns={
        f"{args.label}_Count": f"{args.label.replace(' ', '_')}_Voters",
        f"{args.label}_Percentage": f"Percentage_{args.label.replace(' ', '_')}_Voters",
    })
    result.to_csv(args.output, index=False)
    print(f"Wrote {args.output}")
    print(result)


if __name__ == "__main__":
    main()
