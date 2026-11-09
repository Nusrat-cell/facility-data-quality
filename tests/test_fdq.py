import pandas as pd

from fdq.clean import check, normalise
from fdq.report import opportunity_score, write_excel
from fdq.sample import build


def test_units_are_converted_to_one_scale():
    df = pd.DataFrame({"name": ["a"], "country": ["DK"], "capacity": [2.0], "capacity_unit": ["MLD"]})
    assert normalise(df).loc[0, "capacity_m3_day"] == 2000.0


def test_country_names_are_unified():
    df = pd.DataFrame({"name": [" x "], "country": ["USA"], "capacity": [1], "capacity_unit": ["m3/day"]})
    out = normalise(df)
    assert out.loc[0, "country"] == "United States" and out.loc[0, "name"] == "X"


def test_every_bad_row_is_quarantined_with_a_reason_and_none_vanish():
    raw = build()
    clean, bad = check(raw)
    assert len(clean) + len(bad) == len(raw)
    assert (bad["reason"] != "").all()
    assert {"missing capacity", "coordinates out of range", "duplicate record (same name and country)"} <= set(
        r.strip() for reasons in bad["reason"] for r in reasons.split(";"))


def test_clean_rows_have_valid_coordinates_and_dates():
    clean, _ = check(build())
    assert clean["lat"].between(-90, 90).all() and clean["permit_expiry"].notna().all()


def test_score_prefers_large_plants_with_soon_expiring_permits():
    t = pd.Timestamp("2026-11-02")
    big_soon = pd.Series({"capacity_m3_day": 60000, "permit_expiry": pd.Timestamp("2027-06-01")})
    small_late = pd.Series({"capacity_m3_day": 1000, "permit_expiry": pd.Timestamp("2031-06-01")})
    assert opportunity_score(big_soon, t) > opportunity_score(small_late, t)


def test_excel_has_three_sheets(tmp_path):
    clean, bad = check(build())
    p = tmp_path / "x.xlsx"
    write_excel(clean, bad, str(p))
    assert pd.ExcelFile(p).sheet_names == ["Summary", "Top 50 leads", "Data quality log"]
