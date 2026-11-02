# India Education Institutions & Cities, Usage Guide

Hands-on guide for the India Education Institutions & Cities dataset. See the dataset description for full stats and sources.

## Files

| File | Contents | Rows |
| --- | --- | --- |
| `india_colleges.csv` | Colleges, universities, IITs, NITs, IIMs | 1,203 |
| `india_schools.csv` | Well-known schools | 247 |
| `india_cities.csv` | Cities/towns, all states & UTs | 4,242 |
| `india_city_coords.csv` | lat/lng lookup (lowercase, w/ aliases) | 3,708 |

## Quickstart

```python
import pandas as pd
colleges = pd.read_csv("india_colleges.csv")
schools  = pd.read_csv("india_schools.csv")
cities   = pd.read_csv("india_cities.csv")
coords   = pd.read_csv("india_city_coords.csv")
```

## Lookups & joins

City names in `india_city_coords.csv` are lowercase, with aliases (e.g. `bhubaneswar`/`bhubaneshwar`).

```python
coords[coords["city"] == "mumbai"]

colleges["city_key"] = colleges["city"].str.lower().str.strip()
merged = colleges.merge(coords, left_on="city_key", right_on="city", how="inner")
# Colleges with coordinates: 710 / 1203 (unmatched cities dropped)
```

## Map colleges (Plotly)

```python
import plotly.express as px
fig = px.scatter_mapbox(merged, lat="lat", lon="lng", color="type",
    size="rating", hover_name="name", zoom=3.4, height=700)
fig.update_layout(mapbox_style="open-street-map")
fig.show()
```

## Distance between cities

```python
import math

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))
```

## JavaScript / TypeScript

Same data via the `india-edu-cities-data` npm package (case-insensitive city lookup).

```bash
npm install india-edu-cities-data
```
```js
const { getCityCoords } = require("india-edu-cities-data");
getCityCoords("Mumbai"); // { lat: 19.054999, lng: 72.8692035 }
```

## How it was built

- **Colleges & schools:** NIRF 2024 rankings, curated directories, manual checks.
- **Cities:** from `indiaCities.json`, used by the [Unihaul](https://unihaul.vercel.app) and [SRM NCR Webring](https://github.com/io-PEAK/srm-ncr-webring) projects.
- **Coordinates:** Nominatim (OpenStreetMap) geocoder, queried as `"city, state, India"` (~1 req/sec, per Nominatim policy). Script: [`geocode-cities.js`](https://github.com/io-PEAK/srm-ncr-webring/blob/main/scripts/geocode-cities.js). 3,697/4,242 cities resolved; unresolved ones dropped. Keys lowercased, aliases added (e.g. `bhubaneswar`/`bhubaneshwar`).

## License

Free for personal and commercial use. Attribution appreciated, not required.

---
Built for [Unihaul](https://unihaul.vercel.app), a marketplace for Indian students, and the [SRM NCR Webring](https://io-peak.github.io/srm-ncr-webring/).