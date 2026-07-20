"""
Rebuild app/facilities/facilities.json from the CFL, optionally adding
hospitals you geocoded and VERIFIED yourself.

    python build_facilities.py

Reads:
  - senegal_consolidated_facilitylist20230521.xlsx   (the CFL)
  - geocoded_hospitals.csv                           (optional; only rows marked VERIFIED=yes)

Writes:
  - app/facilities/facilities.json
"""

import json
import os

import pandas as pd

CFL_PATH = "senegal_consolidated_facilitylist20230521.xlsx"
GEOCODED_PATH = "geocoded_hospitals.csv"
OUT_PATH = "app/facilities/facilities.json"

EXCLUDE_TYPES = {"autre"}


def main():
    df = pd.read_excel(CFL_PATH)

    has_gps = df["group_latitude"].notna() & df["group_longitude"].notna()
    not_excluded = ~df["group_fac_type"].isin(EXCLUDE_TYPES)
    not_flagged = df["data_flagged"].isna()

    clean = df[has_gps & not_excluded & not_flagged].copy()

    facilities = []
    for _, r in clean.iterrows():
        facilities.append({
            "id": str(r["match_id"]),
            "name": str(r["match_name"]).strip().title(),
            "type": str(r["group_fac_type"]).strip(),
            "region": str(r["region"]).strip(),
            "lat": float(r["group_latitude"]),
            "lon": float(r["group_longitude"]),
            "gps_source": "cfl",
        })

    print(f"From CFL: {len(facilities)} facilities")

    # --- Add hospitals you geocoded and verified ---
    added = 0
    if os.path.exists(GEOCODED_PATH):
        g = pd.read_csv(GEOCODED_PATH)
        verified = g[
            g["VERIFIED"].astype(str).str.strip().str.lower().eq("yes")
            & g["lat"].notna()
            & g["lon"].notna()
        ]
        for _, r in verified.iterrows():
            facilities.append({
                "id": str(r["match_id"]),
                "name": str(r["name"]).strip().title(),
                "type": "hopital",
                "region": str(r["region"]).strip(),
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "gps_source": "manually_geocoded",
            })
            added += 1
        print(f"Added {added} manually geocoded + verified hospitals")
    else:
        print(f"(no {GEOCODED_PATH} found — skipping manual additions)")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(facilities, f, ensure_ascii=False, indent=1)

    print(f"\nWrote {OUT_PATH}: {len(facilities)} facilities total")

    # Coverage report
    hosp = [f for f in facilities if f["type"] == "hopital"]
    regions_with_hosp = {f["region"] for f in hosp}
    all_regions = set(df["region"].dropna().unique())
    print(f"Hospitals: {len(hosp)}")
    missing = sorted(all_regions - regions_with_hosp)
    print("Regions with NO geolocated hospital:", missing if missing else "none")


if __name__ == "__main__":
    main()