"""Name-match logic shared by all scripts.

Matching is intentionally loose: a voter counts for a category if their
first name OR last name appears in that category's first-name OR last-name
set. This catches partial lists (e.g. a voter named "Mohammed Ali" matches a
list that contains only "Mohammed") but will over-count very common names.
"""
import pandas as pd


def build_category_name_lists(names_df: pd.DataFrame) -> dict:
    """Group a name-category DataFrame into {category: {first_names, last_names}}."""
    categories = {}
    for category in names_df["Category"].unique():
        subset = names_df[names_df["Category"] == category]
        categories[category] = {
            "first_names": set(
                subset["First Name"].dropna().astype(str).str.strip()
            ),
            "last_names": set(
                subset["Last Name"].dropna().astype(str).str.strip()
            ),
        }
    return categories


def is_in_category(row, category_names: dict) -> bool:
    """Return True if the voter row's first or last name is in either set."""
    first = str(row.get("Name First", "")).strip()
    last = str(row.get("Name Last", "")).strip()
    if not first and not last:
        return False
    firsts = category_names["first_names"]
    lasts = category_names["last_names"]
    return first in firsts or first in lasts or last in firsts or last in lasts
