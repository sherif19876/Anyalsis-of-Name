"""Find names in an unclassified CSV that are NOT in a classified CSV.

Both files are assumed to have the name in the first column.

Usage:
    python scripts/02_find_unique_names.py --classified classified.csv \
        --unclassified unknown.csv --out missing.csv
"""
import argparse
import pandas as pd

from voter_analysis.cleaning import normalize_name


def find_unique(classified_file: str, unclassified_file: str, output_file: str) -> None:
    classified = pd.read_csv(classified_file, usecols=[0])
    unclassified = pd.read_csv(unclassified_file, usecols=[0])

    classified.columns = ["name"]
    unclassified.columns = ["name"]

    classified["clean"] = classified["name"].apply(normalize_name)
    unclassified["clean"] = unclassified["name"].apply(normalize_name)

    unique = set(unclassified["clean"]) - set(classified["clean"])
    result = (
        unclassified[unclassified["clean"].isin(unique)][["name"]]
        .drop_duplicates()
    )

    result.to_csv(output_file, index=False)
    print(f"Wrote {len(result)} unique names to {output_file}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--classified", required=True)
    p.add_argument("--unclassified", required=True)
    p.add_argument("--out", dest="output", default="missing_names.csv")
    args = p.parse_args()
    find_unique(args.classified, args.unclassified, args.output)


if __name__ == "__main__":
    main()
