import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ================= CONFIG LOAD =================
CONFIG_FILE = "config.yml"

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TIMEZONE = config.get("timezone", "Asia/Kathmandu")
DATA_FOLDER = Path(config.get("data_folder", "date"))
OUTPUT_FILE = config.get("output_file", "index.html")
SITE_TITLE = config.get("site_title", "Nepali Calendar Today")

TZ = ZoneInfo(TIMEZONE)

# ================= CURRENT TIME (NPT) =================
now = datetime.now(TZ)
year_month = now.strftime("%Y%m")          # e.g. 202601
today_ad = now.strftime("%Y-%m-%d")        # e.g. 2026-01-13

json_file = DATA_FOLDER / f"{year_month}.json"

print("===================================")
print("Nepali Time:", now)
print("Looking for JSON:", json_file)
print("===================================")

# ================= SAFE FALLBACK =================
if not json_file.exists():
    print("JSON file NOT found. Writing fallback index.html")

    fallback_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{SITE_TITLE}</title>
</head>
<body>
<h2>Calendar data not available</h2>
<p>Please check back later.</p>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(fallback_html)

    exit(0)

# ================= LOAD JSON (AUTO-DETECT FORMAT) =================
with open(json_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

if isinstance(raw, list):
    if len(raw) == 0:
        raise ValueError("Calendar JSON array is empty")
    data = raw[0]
elif isinstance(raw, dict):
    data = raw
else:
    raise ValueError("Unsupported calendar JSON format")

# ================= EXTRACT DATA =================
month_info = data.get("month_info", {})
days = data.get("days", [])

ad_month = month_info.get("ad_month", "")
ad_year = month_info.get("ad_year", "")
bs_months = ", ".join(month_info.get("bs_months", []))

# ================= BUILD TABLE ROWS =================
rows_html = ""

for d in days:
    ad = d.get("ad", "")
    bs = d.get("bs", "")
    day = d.get("day", "")
    event = d.get("event") or ""

    row_class = "today" if ad == today_ad else ""

    rows_html += f"""
    <tr class="{row_class}">
        <td>{ad}</td>
        <td>{bs}</td>
        <td>{day}</td>
        <td>{event}</td>
    </tr>
    """

# ================= FINAL HTML =================
html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{SITE_TITLE}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f4f4f4;
}}
.container {{
    max-width: 1000px;
    margin: auto;
    background: #ffffff;
    padding: 20px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    border: 1px solid #cccccc;
    padding: 8px;
    text-align: left;
}}
th {{
    background: #222;
    color: #ffffff;
}}
.today {{
    background: #fff3cd;
    font-weight: bold;
}}
</style>
</head>
<body>

<div class="container">
    <h1>{SITE_TITLE}</h1>

    <p>
        <strong>AD:</strong> {ad_month} {ad_year} |
        <strong>BS:</strong> {bs_months}
    </p>

    <table>
        <tr>
            <th>AD Date</th>
            <th>BS Date</th>
            <th>Day</th>
            <th>Event</th>
        </tr>
        {rows_html}
    </table>

    <p style="margin-top:10px;color:#777;">
        Updated: {now.strftime('%Y-%m-%d %H:%M')} (NPT)
    </p>
</div>

</body>
</html>
"""

# ================= WRITE index.html =================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ index.html generated successfully")
