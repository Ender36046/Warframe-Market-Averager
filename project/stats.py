import requests
import json
from datetime import datetime, timezone, timedelta

def get_item_stats(slug):
    url = f"https://api.warframe.market/v1/items/{slug}/statistics"
    headers = {"Accept-Language": "en"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data["payload"]


def median_prices(slug, mod_rank=None):
    stats = get_item_stats(slug)
    closed_stats = stats["statistics_closed"]
    recent = closed_stats["48hours"]
    historical = closed_stats["90days"]

    historical_median = 0
    recent_median = 0
    recent_moving_average = 0
    num_recent = 0
    num_historical = 0

    super_recent_median = 0
    num_sr = 0

    for data_point in historical:
        if(mod_rank != None and data_point["mod_rank"] != mod_rank):
            continue
        historical_median += data_point["median"]
        num_historical+=1


    for data_point in recent:
        if(mod_rank != None and data_point["mod_rank"] != mod_rank):
            continue
        recent_median +=data_point["median"]
        recent_moving_average +=data_point["wa_price"]
        num_recent+=1

        now = datetime.now(timezone.utc)

        
        if(timedelta(0) <= (now - datetime.fromisoformat(data_point["datetime"])) <= timedelta(hours=12)):
            super_recent_median+= data_point["median"]
            num_sr +=1
    
    return{
        "historical_med":historical_median//num_historical,
        "recent_med":recent_median//num_recent,
        "recent_wa": recent_moving_average//num_recent,
        "sr_med":super_recent_median//num_sr
    }