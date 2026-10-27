"""Match cleaned names against a reference CSV across multiple voter files.

Reference CSV must have columns 'First' and 'Last'.
Voter files are Excel; by default last name is column 2 (3rd) and
first name is column 4 (5th), matching the original FLA-style layout.

Usage:
    python scripts/03_match_voter_files.py --names Names_Split.csv \
        --voter-files FLA.xlsx STJ.xlsx VOL.xlsx --out-prefix Namesfin
"""
import argparse
import os
import pandas as pd

from voter_analysis.cleaning import clean_name


def process_file(
    voter_path: str,
    names_df: pd.DataFrame,
    out_prefix: str,
    last_col: int,
    first_col: int,
    has_header: bool,
) -> None:
    header = 0 if has_header else None
    df = pd.read_excel(voter_path, dtype=str, header=header)

    df["First_Clean"] = df.iloc[:, first_col].apply(clean_name)
    df["Last_Clean"] = df.iloc[:, last_col].apply(clean_name)
    df["Full_Clean"] = df["First_Clean"] + "_" + df["Last_Clean"]

    ref = set(names_df["Full_Clean"])
    mask = df["Full_Clean"].isin(ref)

    matched = df[mask].drop(columns=["First_Clean", "Last_Clean", "Full_Clean"])
    found = set(df.loc[mask, "Full_Clean"])
    not_found = names_df[~names_df["Full_Clean"].isin(found)]

    base = os.path.splitext(os.path.basename(voter_path))[0]
    matched_file = f"{out_prefix}_{base}.xlsx"
    notfound_file = f"{out_prefix}_{base}_NotFound.xlsx"

    matched.to_excel(matched_file, index=False, header=has_header)
    not_found[["First", "Last"]].to_excel(notfound_file, index=False)

    print(f"{voter_path}: {len(matched)} matched, {len(not_found)} not found")
    print(f"  → {matched_file}")
    print(f"  → {notfound_file}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--names", required=True, help="Reference CSV with First, Last columns")
    p.add_argument("--voter-files", nargs="+", required=True)
    p.add_argument("--out-prefix", default="Namesfin")
    p.add_argument("--first-col", type=int, default=4)
    p.add_argument("--last-col", type=int, default=2)
    p.add_argument("--has-header", action="store_true")
    args = p.parse_args()

    names_df = pd.read_csv(args.names, dtype=str)
    if not {"First", "Last"}.issubset(names_df.columns):
        raise SystemExit("Reference CSV must contain columns 'First' and 'Last'.")

    names_df["First_Clean"] = names_df["First"].apply(clean_name)
    names_df["Last_Clean"] = names_df["Last"].apply(clean_name)
    names_df["Full_Clean"] = names_df["First_Clean"] + "_" + names_df["Last_Clean"]

    for f in args.voter_files:
        process_file(
            f, names_df, args.out_prefix,
            args.last_col, args.first_col, args.has_header,
        )


if __name__ == "__main__":
    main()
