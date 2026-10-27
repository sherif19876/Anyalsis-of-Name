"""Name and precinct string cleaning utilities."""
import re
import pandas as pd

_LETTERS_ONLY = re.compile(r"[^a-z]")
_PRECINCT_SUFFIX = re.compile(r"\.1$")


def clean_name(value) -> str:
    """Aggressive cleaning: keep only lowercase a-z. Use for match keys."""
    if pd.isna(value):
        return ""
    return _LETTERS_ONLY.sub("", str(value).lower())


def normalize_name(value) -> str:
    """Gentle cleaning: lowercase, trim, collapse internal whitespace.

    Use for human-readable comparisons and display.
    """
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().lower().split())


def clean_precinct(value) -> str:
    """Strip whitespace and a trailing '.1' (or '.N') suffix from a precinct."""
    return _PRECINCT_SUFFIX.sub("", str(value).strip())


def clean_precinct_series(series: pd.Series) -> pd.Series:
    """Vectorised version of :func:`clean_precinct` for a DataFrame column."""
    return series.astype(str).str.strip().str.replace(r"\.1$", "", regex=True)
