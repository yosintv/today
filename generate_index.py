import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# Load config
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TZ = ZoneInfo(config["timezone"])
DATA_FOLDER = Path(config["data_folder"])
OUTPUT_FILE = config["output_file"]

now = datetime.now(TZ)
year_month = now.strftime("%Y%m")
today_ad = now.strftime("%Y-%m-%d")

json_file = DATA_FOLDER / f"{year_month}.json"

if not json_file.exists():
    print("No calendar data for this month.")
    exit(0)

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)[0]

month = data["month_info"]
days = data["days"]

rows = ""
for d in days:
    event = d["event"] or ""
    cls = "today" if d["ad"] == today_ad else ""
    rows += f"""
    <tr class="{cls}">
      <td>{d['ad']}</td>
      <td>{d['bs']}</td>
      <td>{d['day']}</td>
      <td>{event}</td>
    </tr>
    """

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{config['site_title']}</title>
<style>
body{{font-family:Arial;background:#f4f4f4}}
.container{{max-width:900px;margin:auto;background:#fff;padding:20px}}
table{{width:100%;border-collapse:collapse}}
th,td{{border:1px solid #ccc;padding:8px}}
th{{background:#111;color:#fff}}
.today{{background:#fff3cd;font-weight:bold}}
</style>
</head>
<body>
<div class="container">
<h1>{config['site_title']}</h1>
<p>
AD: {month['ad_month']} {month['ad_year']} |
BS: {", ".join(month['bs_months'])}
</p>
<table>
<tr><th>AD</th><th>BS</th><th>Day</th><th>Event</th></tr>
{rows}
</table>
<p>Updated: {now.strftime('%Y-%m-%d %H:%M')} (NPT)</p>
</div>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated")
