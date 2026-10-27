"""District-level counts and percentages per name category.

Canonical analysis script. Use this unless you have exactly one category
(in which case 06 is a thin wrapper around the same library).

Usage:
    python scripts/05_analyze_by_category.py \
        --voter data/raw/Vlist.csv \
        --districts data/raw/precincts_city_council_districts.csv \
        --categories data/raw/all_name_categories.csv \
        --out data/output/voter_analysis_by_district_and_category.csv
"""
import argparse

from voter_analysis.io import (
    load_voter_file, load_districts, load_name_categories,
)
from voter_analysis.matching import build_category_name_lists
from voter_analysis.aggregation import aggregate_by_district


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--voter", required=True)
    p.add_argument("--districts", required=True)
    p.add_argument("--categories", required=True)
    p.add_argument("--out", dest="output",
                   default="voter_analysis_by_district_and_category.csv")
    p.add_argument("--district-col", default="City_Council_District")
    p.add_argument("--id-col", default="Voter ID")
    args = p.parse_args()

    print("Loading voter file…")
    voters = load_voter_file(args.voter)
    print(f"  {len(voters)} voters")

    print("Loading districts…")
    districts = load_districts(args.districts)

    print("Loading categories…")
    cat_df = load_name_categories(args.categories)
    lookup = build_category_name_lists(cat_df)
    print(f"  categories: {list(lookup)}")

    result = aggregate_by_district(
        voters, districts, lookup,
        district_col=args.district_col, id_col=args.id_col,
    )
    result.to_csv(args.output, index=False)
    print(f"Wrote {args.output} ({len(result)} districts)")
    print(result.head())


if __name__ == "__main__":
    main()
