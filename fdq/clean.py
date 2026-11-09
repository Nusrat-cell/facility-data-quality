"""Cleaning rules. Rows that fail a blocking check go to a quarantine table with a reason, never silently dropped."""
from __future__ import annotations

import pandas as pd

COUNTRY_MAP = {"DK": "Denmark", "Danmark": "Denmark", "DE": "Germany", "Deutschland": "Germany",
               "SE": "Sweden", "Sverige": "Sweden", "US": "United States", "USA": "United States",
               "NL": "Netherlands", "Nederland": "Netherlands"}
TO_M3_PER_DAY = {"m3/day": 1.0, "MLD": 1000.0, "gal/day": 0.003785}  # megalitres/day = 1000 m3/day


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["name"] = out["name"].str.strip().str.title()
    out["country"] = out["country"].str.strip().replace(COUNTRY_MAP)
    factor = out["capacity_unit"].map(TO_M3_PER_DAY)
    out["capacity_m3_day"] = (out["capacity"] * factor).round(1)
    if "permit_expiry" in out:
        out["permit_expiry"] = pd.to_datetime(out["permit_expiry"], errors="coerce")
    return out


def check(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean rows, quarantined rows with a reason)."""
    df = normalise(df)
    reasons = pd.Series("", index=df.index)

    def flag(mask: pd.Series, text: str) -> None:
        nonlocal reasons
        reasons = reasons.where(~mask, reasons.where(reasons == "", reasons + "; ") + text)

    flag(df.duplicated(["name", "country"], keep="first"), "duplicate record (same name and country)")
    flag(df["capacity"].isna(), "missing capacity")
    flag(~df["lat"].between(-90, 90) | ~df["lon"].between(-180, 180), "coordinates out of range")
    flag(df["permit_expiry"].isna(), "permit date missing or unreadable")
    bad = reasons != ""
    quarantined = df[bad].assign(reason=reasons[bad])
    return df[~bad].reset_index(drop=True), quarantined.reset_index(drop=True)
