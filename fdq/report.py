"""Builds the client-ready Excel file: summary, ranked opportunities, data quality log."""
from __future__ import annotations

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER = PatternFill("solid", fgColor="1F4E9C")


def opportunity_score(row: pd.Series, today: pd.Timestamp) -> float:
    """Simple, explainable score: bigger plants and permits expiring soon are better leads."""
    months = max((row["permit_expiry"] - today).days / 30.4, 0)
    size = min(row["capacity_m3_day"] / 50000, 1.0)
    urgency = 1.0 if months <= 24 else 0.5 if months <= 48 else 0.2
    return round(60 * size + 40 * urgency, 1)


def write_excel(clean: pd.DataFrame, quarantined: pd.DataFrame, path: str, today: str = "2026-11-02") -> None:
    t = pd.Timestamp(today)
    leads = clean.assign(score=clean.apply(opportunity_score, axis=1, today=t)).sort_values("score", ascending=False)
    leads = leads[["facility_id", "name", "country", "type", "capacity_m3_day", "permit_expiry", "score"]].head(50)
    leads["permit_expiry"] = leads["permit_expiry"].dt.date
    summary = pd.DataFrame({
        "Measure": ["Records received", "Records used", "Records set aside (see Data quality log)", "Countries covered",
                    "Median capacity (m3/day)", "Permits expiring within 24 months"],
        "Value": [len(clean) + len(quarantined), len(clean), len(quarantined), clean["country"].nunique(),
                  round(clean["capacity_m3_day"].median(), 1), int((clean["permit_expiry"] <= t + pd.DateOffset(months=24)).sum())],
    })
    log = quarantined[["facility_id", "name", "country", "reason"]]
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        for name, frame in (("Summary", summary), ("Top 50 leads", leads), ("Data quality log", log)):
            frame.to_excel(xl, sheet_name=name, index=False)
            ws = xl.sheets[name]
            ws.freeze_panes = "A2"
            for c in ws[1]:
                c.font = Font(bold=True, color="FFFFFF"); c.fill = HEADER; c.alignment = Alignment(horizontal="left")
            for i, col in enumerate(frame.columns, 1):
                width = max(len(str(col)), *(len(str(v)) for v in frame[col].head(200))) + 2
                ws.column_dimensions[get_column_letter(i)].width = min(width, 60)
