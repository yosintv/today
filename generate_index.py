import json
import os
from datetime import datetime, timedelta

def generate_html():
    # Calculate Nepal Time (UTC + 5:45)
    npt_now = datetime.utcnow() + timedelta(hours=5, minutes=45)
    today_str = npt_now.strftime('%Y-%m-%d')
    file_key = npt_now.strftime('%Y%m')  # e.g., "202512"
    
    file_path = f"date/{file_key}.json"
    
    if not os.path.exists(file_path):
        print(f"Error: Data for {file_key} not found.")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)[0]

    # Find today's specific entry
    today_data = next((d for d in data['days'] if d['ad'] == today_str), None)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Today's Date - {npt_now.strftime('%B %Y')}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; text-align: center; background: #f4f4f9; padding: 50px; }}
            .card {{ background: white; padding: 30px; border-radius: 15px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; margin-bottom: 5px; }}
            .bs-date {{ font-size: 2em; color: #e74c3c; font-weight: bold; }}
            .ad-date {{ font-size: 1.2em; color: #7f8c8d; }}
            .event {{ margin-top: 20px; padding: 10px; background: #fff3cd; border-radius: 5px; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Today in Nepal</h1>
            <p class="bs-date">{today_data['bs'] if today_data else 'N/A'}</p>
            <p class="ad-date">{today_data['ad'] if today_data else today_str} ({today_data['day'] if today_data else ''})</p>
            {f'<div class="event"><b>Event:</b> {today_data["event"]}</div>' if today_data and today_data['event'] else ''}
            <p style="margin-top:20px; font-size:0.8em;">Month: {data['month_info']['bs_months'][0]} / {data['month_info']['ad_month']}</p>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html()
