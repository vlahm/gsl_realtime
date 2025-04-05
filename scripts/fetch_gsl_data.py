import requests
import pandas as pd
import json
from datetime import datetime
import os
from io import StringIO


south_arm = "10010000"
north_arm = "10010100"
salin = "405356112205601"
start_date = "2000-01-01"
end_date = datetime.utcnow().strftime("%Y-%m-%d")

fallback_path = "data/"


def retrieve_elev(gage_id, start_date, end_date, param_code):

    url = (
        "https://waterservices.usgs.gov/nwis/dv/?format=json"
        f"&sites={gage_id}"
        f"&startDT={start_date}&endDT={end_date}"
        f"&parameterCd={param_code}&siteStatus=all"
    )

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    records = data["value"]["timeSeries"][0]["values"][0]["value"]
    df = pd.DataFrame(records)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["dateTime"])
    # df["date"] = df["dateTime"].dt.strftime("%Y-%m-%d")
    # df["date"] = df["dateTime"].dt.date
    # df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    df = df.drop(["dateTime", "qualifiers"], axis=1)
    df = df.dropna()
    df.to_json(fallback_path + gage_id + ".json", orient="records")
    return df


def retrieve_salin(gage_id, start_date, end_date):

    url = (
        "https://api.waterdata.usgs.gov/samples-data/results/narrow?mimeType=text%2Fcsv&monitoringLocationIdentifier=USGS-"
        f"{gage_id}&characteristicUserSupplied=Salinity%252C%2520water&siteTypeCode=LK&stateFips=US:49&activityStartDateLower="
        f"{start_date}&activityStartDateUpper={end_date}"
    )

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = StringIO(r.text)
    df = pd.read_csv(data)
    df = df[["Activity_StartDate", "Result_Measure"]]
    df.rename(
        columns={"Activity_StartDate": "date", "Result_Measure": "value"}, inplace=True
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    # df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df.dropna()
    df.to_json(fallback_path + gage_id + ".json", orient="records")
    return df


try:
    dfN = retrieve_elev(north_arm, start_date, end_date, "62614")
    dfS = retrieve_elev(south_arm, start_date, end_date, "62614")
    dfsal = retrieve_salin(salin, start_date, end_date)
    print("Data successfully updated.")
except Exception as e:
    print(f"Error fetching data: {e}")
    if os.path.exists(fallback_path + south_arm + ".json"):
        print("Using cached data.")
        dfS = pd.read_json(
            fallback_path + south_arm + ".json", orient="records", convert_dates=True
        )
        dfN = pd.read_json(
            fallback_path + north_arm + ".json", orient="records", convert_dates=True
        )
        dfsal = pd.read_json(
            fallback_path + salin + ".json", orient="records", convert_dates=True
        )
    else:
        raise RuntimeError("No data available: fetch failed and no cache found.")

df = pd.merge(dfS, dfN, how="left", on="date", suffixes=["_s", "_n"])
df["value"] = (df["value_s"] * 0.64) + (df["value_n"] * 0.36)
df = df.drop(["value_s", "value_n"], axis=1)
df.to_json(fallback_path + "avg.json", orient="records")

sal_recent = dfsal.loc[dfsal["date"].idxmax(), "date"]
current_salin = dfsal[dfsal["date"] == sal_recent]["value"].mean() / 10

avg_lvl = df.loc[df["date"].idxmax(), "value"]
area = 21787.72 * avg_lvl - 90692145
volume = 15490.58 * avg_lvl**2 - 129149899.44 * avg_lvl + 269191309891.96
area_at_4207 = 1375869
volume_at_4207 = 24088680

stats = pd.DataFrame(
    {
        "level_n": [str(round(dfN.loc[dfN["date"].idxmax(), "value"], 1)) + "'"],
        "level_s": [str(round(dfS.loc[dfS["date"].idxmax(), "value"], 1)) + "'"],
        "below_healthy": [str(round(4198 - avg_lvl, 1)) + "'"],
        "pct_exposed": [str(round(100 - (area * 100 / area_at_4207), 1)) + "%"],
        "pct_volume": [str(round(volume * 100 / volume_at_4207, 1)) + "%"],
        "sqmi_exposed": [str(round((area_at_4207 - area) * 0.0015625, 1)) + " mi²"],
        "sqmi_exposed_alt": [str(round((area_at_4207 - area) * 0.0015625, 1))],
        "salin": [str(round(current_salin, 1)) + "%"],
        "salin_record_date": sal_recent.strftime("%Y-%m-%d"),
    },
    index=["summary"],
)
# ).applymap(lambda x: round(x, 1))

stats.to_json(fallback_path + "stats.json", orient="records")
