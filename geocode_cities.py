"""
Geocode Senegalese cities/towns for the manual-location feature.

"""

import json
import os
import time
import urllib.parse
import urllib.request

INPUT = "cities_to_geocode.txt"
OUT = "app/facilities/cities.json"

HEADERS = {"User-Agent": "TelemedicinePFE/1.0 (student project; contact: darodiengsarr@gmail.com)"}
VIEWBOX = "-17.6,16.7,-11.3,12.3"  # Senegal bounding box


def geocode(city, region):
    params = {
        "q": f"{city}, {region}, Senegal",
        "format": "json",
        "limit": 1,
        "countrycodes": "sn",
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
    with open(INPUT, encoding="utf-8") as f:
        entries = [line.strip().split("|") for line in f if line.strip()]

    cities = []
    found = 0
    for city, region in entries:
        print(f"  {city} ({region})")
        res = geocode(city, region)
        time.sleep(1.1)  # Nominatim: 1 req/sec
        if res:
            lat, lon, disp = res
            print(f"    -> {lat:.5f}, {lon:.5f}")
            found += 1
        else:
            lat = lon = disp = None
            print("    -> NOT FOUND")
        cities.append({
            "city": city,
            "region": region,
            "lat": round(lat, 5) if lat else None,
            "lon": round(lon, 5) if lon else None,
            "osm_result": disp,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # Keep only successfully geocoded ones in the final file.
    good = [c for c in cities if c["lat"] is not None]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(good, f, ensure_ascii=False, indent=1)

    print(f"\nGeocoded {found}/{len(entries)}. Wrote {len(good)} to {OUT}")
    print("Review the coordinates before relying on them.")


if __name__ == "__main__":
    main()