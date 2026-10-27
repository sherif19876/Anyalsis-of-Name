"""Export full voter rows that match a target name list, joined to districts.

Usage:
    python scripts/04_extract_target_voters.py \
        --voter data/raw/voter_data.csv \
        --names data/raw/target_names.csv \
        --districts data/raw/precincts_city_council_districts.csv \
        --out data/output/target_group_voters_filtered.csv
"""
import argparse
import pandas as pd

from voter_analysis.io import load_voter_file, load_target_names, load_districts
from voter_analysis.aggregation import extract_matched_rows

OUTPUT_COLUMNS = [
    "Voter ID", "Name Last", "Name Suffix", "Name First", "Name Middle",
    "Requested public records exemption", "Residence Address Line 1",
    "Residence Address Line 2", "Residence City (USPS)", "Residence State",
    "Residence Zipcode", "Mailing Address Line 1", "Mailing Address Line 2",
    "Mailing Address Line 3", "Mailing City", "Mailing State",
    "Mailing Zipcode", "Mailing Country", "Gender", "Race", "Birth Date",
    "Registration Date", "Party Affiliation", "Precinct", "Precinct Group",
    "Precinct Split", "Precinct Suffix", "Voter Status",
    "Congressional District", "House District", "Senate District",
    "County Commission District", "School Board District",
]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--voter", required=True)
    p.add_argument("--names", required=True)
    p.add_argument("--districts", default=None)
    p.add_argument("--out", dest="output", default="target_group_voters_filtered.csv")
    p.add_argument("--encoding", default="utf-8-sig")
    args = p.parse_args()

    print("Loading voter file…")
    voters = load_voter_file(args.voter, encoding=args.encoding)
    print(f"  {len(voters)} voters")

    print("Loading target names…")
    first_set, last_set = load_target_names(args.names)
    print(f"  {len(first_set)} first names, {len(last_set)} last names")

    matched = extract_matched_rows(voters, first_set, last_set)
    print(f"  {len(matched)} matching voters")

    if args.districts:
        districts = load_districts(args.districts)
        matched = pd.merge(matched, districts, on="Precinct", how="left")

    existing = [c for c in OUTPUT_COLUMNS if c in matched.columns]
    matched[existing].to_csv(args.output, index=False)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
