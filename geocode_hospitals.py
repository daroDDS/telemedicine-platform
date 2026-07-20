"""
Geocode the hospitals missing GPS coordinates in the Senegal CFL.

Run this on YOUR machine (needs internet access to Nominatim).

    python geocode_hospitals.py

It writes 'geocoded_hospitals.csv' for you to REVIEW before use.
Nothing is added to the app automatically — you verify each result first.
"""

import json
import time
import urllib.parse
import urllib.request

import pandas as pd

CFL_PATH = "senegal_consolidated_facilitylist20230521.xlsx"  # adjust path if needed
OUT_PATH = "geocoded_hospitals.csv"

# Nominatim requires a descriptive User-Agent identifying your app.
HEADERS = {"User-Agent": "TelemedicinePFE/1.0 (student project; contact: darodiengsarr@gmail.com)"}

# Senegal bounding box, so results can't land in another country.
# left,top,right,bottom
VIEWBOX = "-17.6,16.7,-11.3,12.3"


def geocode(query: str):
    """Ask Nominatim for coordinates. Returns (lat, lon, display_name) or None."""
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "sn",      # restrict to Senegal
        "viewbox": VIEWBOX,
        "bounded": 1,
    }
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", "")
    except Exception as e:
        print(f"    error: {e}")
    return None


def main():
    df = pd.read_excel(CFL_PATH)
    hosp = df[df["group_fac_type"] == "hopital"].copy()
    missing = hosp[hosp["group_latitude"].isna() | hosp["group_longitude"].isna()]

    print(f"Hospitals missing GPS: {len(missing)}\n")

    rows = []
    for _, r in missing.iterrows():
        name = str(r["match_name"]).strip()
        region = str(r["region"]).strip()

        # Try a few query phrasings, best first.
        queries = [
            f"hopital {name}, {region}, Senegal",
            f"{name}, {region}, Senegal",
            f"{name} hospital, Senegal",
        ]

        result = None
        used = None
        for q in queries:
            print(f"  querying: {q}")
            result = geocode(q)
            time.sleep(1.1)          # Nominatim: max 1 request/second
            if result:
                used = q
                break

        if result:
            lat, lon, disp = result
            print(f"    -> {lat:.5f}, {lon:.5f}  ({disp[:60]})")
        else:
            lat = lon = disp = None
            print("    -> NOT FOUND")

        rows.append({
            "match_id": r["match_id"],
            "region": region,
            "name": name,
            "query_used": used,
            "lat": lat,
            "lon": lon,
            "osm_result": disp,
            "VERIFIED": "",          # <- you fill this in: yes / no
        })
        print()

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH}")
    print(f"Found: {out['lat'].notna().sum()} / {len(out)}")
    print("\nNEXT: open the CSV, check each coordinate on a map,")
    print("      and put 'yes' in the VERIFIED column for the ones that are correct.")


if __name__ == "__main__":
    main()