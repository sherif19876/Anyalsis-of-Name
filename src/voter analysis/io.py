"""Loaders for voter files, name lists, districts, and name categories."""
import pandas as pd

from .cleaning import clean_precinct_series


def load_voter_file(path: str, encoding: str = "utf-8-sig") -> pd.DataFrame:
    """Load a voter CSV; strip column whitespace and normalise Precinct."""
    df = pd.read_csv(path, encoding=encoding)
    df.columns = df.columns.str.strip()
    if "Precinct" in df.columns:
        df["Precinct"] = clean_precinct_series(df["Precinct"])
    return df


def load_target_names(path: str, encoding: str = "cp1252"):
    """Load a CSV with 'First Name' and 'Last Name' columns.

    Returns two sets of stripped, non-empty strings.
    """
    df = pd.read_csv(path, encoding=encoding)
    first = set(df["First Name"].dropna().astype(str).str.strip())
    last = set(df["Last Name"].dropna().astype(str).str.strip())
    return first, last


def load_districts(path: str) -> pd.DataFrame:
    """Load a precinct-to-district mapping CSV."""
    df = pd.read_csv(path)
    df["Precinct"] = df["Precinct"].astype(str).str.strip()
    return df


def load_name_categories(path: str, encoding: str = "utf-8-sig") -> pd.DataFrame:
    """Load a CSV with 'First Name', 'Last Name', 'Category' columns."""
    df = pd.read_csv(path, encoding=encoding)
    for col in ("First Name", "Last Name", "Category"):
        if col not in df.columns:
            raise ValueError(f"Name category file must contain column '{col}'")
    return df
