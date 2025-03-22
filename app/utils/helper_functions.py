from typing import Any, Dict, List
from fastapi import HTTPException
from app.schemas import settings
import requests
import urllib


ACCESS_TOKEN = settings.access_token
API_VERSION = settings.api_version
CLIENT_ID = settings.client_id
CLIENT_SECRET = settings.client_secret
FB_API_URL = settings.fb_api_url
AD_ACCOUNT_ID = "act_1135898378327369"
CONVERSION_TYPES = {"purchase", "web_in_store_purchase",
                    "offsite_conversion.fb_pixel_purchase"}


def fetch_ad_accounts():
    """
    Fetches ad accounts accessible by the app, with their id, name and status.

    Returns:
        A list of ad accounts, each represented as a dictionary with 'id', 'name' and 'account_status' keys.
        Note: I've already fetch the accounts, and I'm not gonna be using this one, so I'm leaving it here.
        There are 2 accounts, and only one of them seems to have creatives, so I'm gonna use that one for now.
        act_1135898378327369
    """
    url = f"{FB_API_URL}/{API_VERSION}/me/adaccounts"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,account_status"
    }
    data = request_facebook_api(url, params)
    return data.get("data", [])


def request_facebook_api(url: str, params: dict) -> dict:
    """
    Makes a GET request to the Facebook Graph API.

    The function takes a URL and parameters, makes the request and returns the JSON response.
    If the request fails and the error code is 190 (expired access token), the access token is refreshed using the refresh_token function.
    If the refresh fails or the new token is not returned, an HTTPException is raised with a 400 status code.
    If the request fails with an error code other than 190, an HTTPException is raised with a 400 status code.
    """
    global ACCESS_TOKEN
    response = requests.get(url, params=params)
    data = response.json()
    if "error" in data:
        error_code = data["error"].get("code")
        if error_code == 190:
            ACCESS_TOKEN = refresh_token()
            params["access_token"] = ACCESS_TOKEN
            response = requests.get(url, params=params)
            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"])
        else:
            raise HTTPException(status_code=400, detail=data["error"])
    return data


def refresh_token() -> str:
    """
    Refreshes the access token for the Facebook Graph API.

    The function retrieves a new access token using the current access token and client id/secret.
    If the refresh fails or the new token is not returned, an HTTPException is raised.

    Returns:
        str: The new access token.
    """
    url = f"{FB_API_URL}/{API_VERSION}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "fb_exchange_token": ACCESS_TOKEN,
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "error" in data:
        raise HTTPException(
            status_code=400, detail="Token refresh failed: " + str(data["error"]))
    new_token = data.get("access_token")
    if not new_token:
        raise HTTPException(
            status_code=400, detail="Failed to retrieve new access token.")
    return new_token


def fetch_ad_creatives_and_insights():
    """
    Fetches ads from a given ad account, along with their creatives and insights. The ads are filtered to only include active, paused, or archived ads.

    Returns:
        A list of ad data, each represented as a dictionary with the following keys:
            - adcreatives (dict): The ad creative data, with keys for body, object_url, image_url, object_type, and image_hash.
            - insights (dict): The ad insights data, with a key for date_preset and a value of a dictionary with keys for spend, clicks, impressions, reach, actions, and unique_actions.
            - id (str): The ad id.
            - name (str): The ad name.
            - campaign (dict): The campaign data, with keys for id, name, account_id, and objective.
            - adset (dict): The adset data, with keys for id and name.
            - created_time (str): The ad creation time, in ISO 8601 format.

    Raises:
        HTTPException: If there is an error in the API response.
    """
    fields = (
        "adcreatives{body,object_url,image_url,object_type,image_hash},"
        "insights.date_preset(maximum).level(ad).breakdowns(publisher_platform){spend,clicks,impressions,reach,actions,unique_actions},"
        "id,name,"
        "campaign{id,name,account_id,objective},"
        "adset{id,name},"
        "created_time"
    )
    encoded_fields = urllib.parse.quote(fields, safe="(),{}")
    url = f"{FB_API_URL}/{API_VERSION}/{AD_ACCOUNT_ID}/ads"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": encoded_fields,
        "limit": "500",
        "effective_status": "['ACTIVE', 'PAUSED', 'ARCHIVED']"
    }
    data = request_facebook_api(url, params=params)

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return data.get("data", [])


def get_best_creatives():
    """
    Fetches ad creatives and insights from Facebook Ads API, and returns the top performing
    ad creatives based on CTR and conversions.

    The function works by iterating over the ad creatives and calculating their metrics.
    The ad creatives are sorted by their CTR and conversions in descending order.
    The top performing ad creatives are returned as a JSON object.

    Returns:
        A JSON object with a single key "best_creatives", which is an array of objects
        containing the following keys:

            - creative_id (str): The ID of the ad creative.
            - image_hash (str): The hash of the ad creative image.
            - creative_details (dict): The ad creative details, as returned by the Facebook Ads API.
            - metrics (dict): The ad metrics, as calculated by the calculate_metrics function.
            - campaign (dict): The ad campaign, as returned by the Facebook Ads API.
            - adset (dict): The ad set, as returned by the Facebook Ads API.
            - created_time (str): The creation time of the ad, as returned by the Facebook Ads API.
            - name (str): The name of the ad, as returned by the Facebook Ads API.

    Raises:
        HTTPException: If there is an error fetching the data from the Facebook Ads API.
    """
    try:
        all_creatives = fetch_ad_creatives_and_insights()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error fetching merged data: " + str(e))

    aggregated: Dict[str, Dict[str, Any]] = {}

    for record in all_creatives:
        creative_data = record.get("adcreatives", {}).get("data", [])
        if not creative_data:
            continue
        if creative_data[0].get("object_type") == "PRIVACY_CHECK_FAIL" or not creative_data[0].get("image_url"):
            continue
        creative_info = creative_data[0]

        image_hash = creative_info.get("image_hash") or creative_info.get("id")
        if not image_hash:
            continue

        insights_data = record.get("insights", {}).get("data", [])
        metrics = calculate_metrics(insights_data)

        result_record = {
            "creative_id": creative_info.get("id"),
            "image_hash": image_hash,
            "creative_details": creative_info,
            "metrics": metrics,
            "campaign": record.get("campaign"),
            "adset": record.get("adset"),
            "created_time": record.get("created_time"),
            "name": record.get("name")
        }

        if image_hash in aggregated:
            if metrics["ctr"] > aggregated[image_hash]["metrics"]["ctr"]:
                aggregated[image_hash] = result_record
        else:
            aggregated[image_hash] = result_record

    best_creatives = sorted(
        aggregated.values(),
        key=lambda x: (x["metrics"]["ctr"], x["metrics"]["conversions"]),
        reverse=True
    )

    return {"best_creatives": best_creatives}


def calculate_metrics(insights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics from ad insights data.

    Args:
        insights (List[Dict[str, Any]]): Ad insights data, as returned by the Facebook Ads API.

    Returns:
        A dictionary with the following keys:
            - impressions (int): The total number of ad impressions.
            - clicks (int): The total number of ad clicks.
            - spend (float): The total spend on the ad.
            - conversions (int): The total number of conversions (as defined by CONVERSION_TYPES).
            - ctr (float): The clickthrough rate, calculated as (clicks / impressions) * 100.

    Raises:
        ValueError: If the insights data contains invalid values.
    """
    total_impressions = 0
    total_clicks = 0
    total_spend = 0.0
    total_conversions = 0
    for ins in insights:
        try:
            impressions = float(ins.get("impressions", 0))
            clicks = float(ins.get("clicks", 0))
            spend = float(ins.get("spend", 0))
        except ValueError:
            continue

        total_impressions += impressions
        total_clicks += clicks
        total_spend += spend

        actions = ins.get("actions", [])
        for action in actions:
            if action.get("action_type") in CONVERSION_TYPES:
                try:
                    total_conversions += int(action.get("value", 0))
                except ValueError:
                    continue

    ctr = (total_clicks / total_impressions *
           100) if total_impressions > 0 else 0
    return {
        "impressions": total_impressions,
        "clicks": total_clicks,
        "spend": total_spend,
        "conversions": total_conversions,
        "ctr": ctr
    }
