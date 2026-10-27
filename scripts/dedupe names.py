"""Remove duplicate names from an Excel file; report frequency.

Usage:
    python scripts/01_dedupe_names.py --in Book1.xlsx --out names_deduplicated.xlsx
"""
import argparse
import pandas as pd


def dedupe(input_file: str, output_file: str, column_name: str = "Name") -> None:
    df = pd.read_excel(input_file)
    if column_name not in df.columns:
        raise ValueError(f"Excel file must contain a column named '{column_name}'")

    counts = df[column_name].value_counts()
    dupes = counts[counts > 1]
    if not dupes.empty:
        print("Duplicate names found:")
        for name, count in dupes.items():
            print(f"  {name}: {count} times")
    else:
        print("No duplicate names found.")

    df.drop_duplicates(subset=column_name, keep="first").to_excel(
        output_file, index=False
    )
    print(f"Deduplicated names written to {output_file}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="input", default="Book1.xlsx")
    p.add_argument("--out", dest="output", default="names_deduplicated.xlsx")
    p.add_argument("--column", default="Name")
    args = p.parse_args()
    dedupe(args.input, args.output, args.column)


if __name__ == "__main__":
    main()
