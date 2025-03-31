import requests
import pandas as pd
import json
from datetime import datetime

site = "10010000"
parameter_code = "62614"
start_date = "2000-01-01"
end_date = datetime.utcnow().strftime("%Y-%m-%d")

url = (
    "https://waterservices.usgs.gov/nwis/dv/?format=json"
    f"&sites={site}"
    f"&startDT={start_date}&endDT={end_date}"
    f"&parameterCd={parameter_code}&siteStatus=all"
)

fallback_path = "data/gsl_data.json"

try:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    records = data["value"]["timeSeries"][0]["values"][0]["value"]
    df = pd.DataFrame(records)
    df["dateTime"] = pd.to_datetime(df["dateTime"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df.to_json(fallback_path, orient="records", date_format="iso")
    print("Data successfully updated.")
except Exception as e:
    print(f"Error fetching data: {e}")
    if os.path.exists(fallback_path):
        print("Using cached data.")
    else:
        raise RuntimeError("No data available: fetch failed and no cache found.")
