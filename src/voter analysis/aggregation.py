"""District-level aggregation helpers."""
import pandas as pd

from .matching import is_in_category


def aggregate_by_district(
    voters_df: pd.DataFrame,
    districts_df: pd.DataFrame,
    category_lookup: dict,
    district_col: str = "City_Council_District",
    id_col: str = "Voter ID",
) -> pd.DataFrame:
    """Return per-district totals and per-category counts/percentages."""
    merged = pd.merge(voters_df, districts_df, on="Precinct", how="left")
    merged = merged.dropna(subset=[district_col])

    totals = merged.groupby(district_col)[id_col].count()

    out = pd.DataFrame({district_col: totals.index.tolist()})
    out = out.sort_values(district_col).reset_index(drop=True)
    out["Total_Voters"] = out[district_col].map(totals).fillna(0).astype(int)

    for category, name_sets in category_lookup.items():
        mask = merged.apply(lambda row: is_in_category(row, name_sets), axis=1)
        counts = merged[mask].groupby(district_col)[id_col].count()
        out[f"{category}_Count"] = out[district_col].map(counts).fillna(0).astype(int)
        out[f"{category}_Percentage"] = (
            out[f"{category}_Count"] / out["Total_Voters"] * 100
        ).fillna(0).round(2)

    return out


def extract_matched_rows(
    voters_df: pd.DataFrame,
    first_set: set,
    last_set: set,
) -> pd.DataFrame:
    """Return rows where first or last name appears in either target set."""
    def _match(row):
        first = str(row.get("Name First", "")).strip()
        last = str(row.get("Name Last", "")).strip()
        return (
            first in first_set
            or first in last_set
            or last in first_set
            or last in last_set
        )

    mask = voters_df.apply(_match, axis=1)
    return voters_df[mask]
