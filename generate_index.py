import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ---------- Load config ----------
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TZ = ZoneInfo(config["timezone"])
DATA_FOLDER = Path(config["data_folder"])
OUTPUT_FILE = config["output_file"]
SITE_TITLE = config.get("site_title", "Nepali Calendar")

# ---------- Current time (Nepal) ----------
now = datetime.now(TZ)
year_month = now.strftime("%Y%m")
today_ad = now.strftime("%Y-%m-%d")

json_file = DATA_FOLDER / f"{year_month}.json"

print("NPT time:", now)
print("Looking for:", json_file)

# ---------- Fallback if JSON missing ----------
if not json_file.exists():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("<h2>Calendar data not available</h2>")
    print("JSON file not found, index.html written safely")
    exit(0)

# ---------- Load API (ARRAY FORMAT) ----------
with open(json_file, "r", encoding="utf-8") as f:
    api_data = json.load(f)

# ✅ GUARANTEE correct format
if not isinstance(api_data, list) or len(api_data) == 0:
    raise ValueError("Invalid API format: expected array with one object")

data = api_data[0]   # 👈 YOUR API FORMAT

month = data["month_info"]
days = data["days"]

# ---------- Build rows ----------
rows = ""
for d in days:
    event = d["event"] or ""
    today_class = "today" if d["ad"] == today_ad else ""
    rows += f"""
    <tr class="{today_class}">
        <td>{d['ad']}</td>
        <td>{d['bs']}</td>
        <td>{d['day']}</td>
        <td>{event}</td>
    </tr>
    """

# ---------- Generate HTML ----------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{SITE_TITLE}</title>
<style>
body {{ font-family: Arial, sans-serif; background:#f4f4f4; }}
.container {{ max-width:900px; margin:auto; background:#fff; padding:20px; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ border:1px solid #ccc; padding:8px; }}
th {{ background:#111; color:#fff; }}
.today {{ background:#fff3cd; font-weight:bold; }}
</style>
</head>
<body>
<div class="container">
<h1>{SITE_TITLE}</h1>
<p>
<strong>AD:</strong> {month['ad_month']} {month['ad_year']} |
<strong>BS:</strong> {", ".join(month['bs_months'])}
</p>

<table>
<tr>
<th>AD Date</th>
<th>BS Date</th>
<th>Day</th>
<th>Event</th>
</tr>
{rows}
</table>

<p style="color:#777;margin-top:10px;">
Updated: {now.strftime('%Y-%m-%d %H:%M')} (NPT)
</p>
</div>
</body>
</html>
"""

# ---------- Write index.html ----------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html generated successfully")
