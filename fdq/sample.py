"""Builds a SYNTHETIC facility list with the kinds of mess real public datasets contain.

All names, places and numbers are invented for practice. No real facility is described.
"""
import random

import pandas as pd

COUNTRIES = {"Denmark": ["DK", "Danmark"], "Germany": ["DE", "Deutschland"], "Sweden": ["SE", "Sverige"],
             "United States": ["US", "USA"], "Netherlands": ["NL", "Nederland"]}
TYPES = ["Municipal", "Industrial", "Dairy", "Food processing", "Chemical", "Brewery"]


def build(n: int = 300, seed: int = 7) -> pd.DataFrame:
    rnd = random.Random(seed)
    rows = []
    names = [f"Facility {i:03d}" for i in range(1, n + 1)]
    for i, name in enumerate(names):
        country = rnd.choice(list(COUNTRIES))
        label = country if rnd.random() < 0.7 else rnd.choice(COUNTRIES[country])
        unit = rnd.choice(["m3/day", "m3/day", "m3/day", "MLD", "gal/day"])
        capacity = {"m3/day": rnd.randint(500, 80000), "MLD": round(rnd.uniform(0.5, 80), 1),
                    "gal/day": rnd.randint(150000, 20000000)}[unit]
        rows.append({
            "facility_id": f"F{i:04d}",
            "name": name if rnd.random() > 0.05 else name.upper() + " ",
            "country": label,
            "type": rnd.choice(TYPES),
            "capacity": capacity,
            "capacity_unit": unit,
            "lat": round(rnd.uniform(35, 70), 4),
            "lon": round(rnd.uniform(-120, 30), 4),
            "permit_expiry": f"20{rnd.randint(27, 33)}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}",
            "discharge_limit_mg_l": rnd.choice([10, 15, 25, 35, None]),
        })
    df = pd.DataFrame(rows)
    # inject realistic problems
    df.loc[df.sample(12, random_state=1).index, "capacity"] = None
    df.loc[df.sample(6, random_state=2).index, "lat"] = 999.0
    df.loc[df.sample(5, random_state=3).index, "permit_expiry"] = "not available"
    # gallons typed into a row that says m3/day (looks like a normal number, only the size gives it away)
    wrong = df[df.capacity_unit == "m3/day"].sample(4, random_state=6).index
    df.loc[wrong, "capacity"] = df.loc[wrong, "capacity"] * 3785
    df = pd.concat([df, df.sample(10, random_state=4).assign(facility_id=lambda d: d.facility_id + "-dup")], ignore_index=True)
    return df.sample(frac=1, random_state=5).reset_index(drop=True)
