import requests
import json
import time
from datetime import datetime, timezone, timedelta

def get_item_stats(slug):
    url = f"https://api.warframe.market/v1/items/{slug}/statistics"
    headers = {
        "Accept-Language": "en",
        "Platform": "pc",
        "Crossplay": "true"
    }
    resp = requests.get(url, headers=headers)
    time.sleep(0.35)
    data = resp.json()
    return data["payload"]

def get_all_items():
    url = f"https://api.warframe.market/v2/items"
    headers = {
        "Accept-Language": "en",
        "Platform": "pc",
        "Crossplay": "true"
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()["data"]
    return data

def median_prices(stats: dict, mod_rank=None):
    if(mod_rank == -1):
        mod_rank = None
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
        if(mod_rank != None and data_point.get("mod_rank") != mod_rank):
            continue
        historical_median += data_point["median"]
        num_historical+=1


    for data_point in recent:
        if(mod_rank != None and data_point.get("mod_rank") != mod_rank):
            continue
        recent_median +=data_point["median"]
        recent_moving_average +=data_point["wa_price"]
        num_recent+=1

        now = datetime.now(timezone.utc)

        
        if(timedelta(0) <= (now - datetime.fromisoformat(data_point["datetime"])) <= timedelta(hours=12)):
            super_recent_median+= data_point["median"]
            num_sr +=1
    
    return{
        "historical_med": (historical_median / num_historical) if num_historical else None,
        "recent_med": (recent_median / num_recent) if num_recent else None,
        "recent_wa": (recent_moving_average / num_recent) if num_recent else None,
        "sr_med": (super_recent_median / num_sr) if num_sr else None,
    }

def get_current_prices(slug: str, mod_rank = None):
    if(mod_rank == -1):
        mod_rank = None
    url = f"https://api.warframe.market/v2/orders/item/{slug}/top?rank={mod_rank}"
    headers = {
        "Accept-Language": "en",
        "Platform": "pc",
        "Crossplay": "true"
        }
    resp = requests.get(url, headers=headers)
    time.sleep(0.35)
    if resp.json()["data"] == None: return {"sell": None, "buy": None}

    sell_data = resp.json()["data"]["sell"]
    buy_data = resp.json()["data"]["buy"]

    sell_dict = {}
    buy_dict = {}
    
    for order in sell_data:
        sell_dict[order["platinum"]] = sell_dict.get(order["platinum"], 0) + order["quantity"]

    for order in buy_data:
        buy_dict[order["platinum"]] = buy_dict.get(order["platinum"], 0) + order["quantity"]

    return {
        "sell": sell_dict, 
        "buy": buy_dict,
        }

def main():
    #print(get_all_items()[0:5])
    #test = get_item_stats("primed_flow")
    get_current_prices("primed_flow", mod_rank=0)

if __name__ == "__main__":
    main()