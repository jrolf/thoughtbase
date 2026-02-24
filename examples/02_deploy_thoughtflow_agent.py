"""
ThoughtBase: Deploy a ThoughtFlow Agent

This example deploys a multi-function agent that aggregates data about
a US zip code from four external APIs — location, elevation, weather,
and sunrise/sunset — into a single response.

Before running, set your API key:
    export THB_API_KEY="your-key-here"
"""

import json

from thoughtbase import call_agent, deploy_agent


# -- Define the agent code -------------------------------------------------

agent_code = '''
import requests, json

def zipcode_location(zipcode):
    """Look up the city, state, and coordinates for a US zip code."""
    r = requests.get("http://api.zippopotam.us/us/" + str(zipcode))
    loc = r.json()["places"][0]
    return {
        "place": loc["place name"],
        "state": loc["state"],
        "lat": float(loc["latitude"]),
        "lon": float(loc["longitude"]),
    }

def location_elevation(loc):
    """Get the elevation for a lat/lon pair."""
    loc_str = str(loc["lat"]) + "," + str(loc["lon"])
    params = {"locations": loc_str}
    r = requests.get("https://api.open-elevation.com/api/v1/lookup", params=params)
    meters = int(float(r.json()["results"][0]["elevation"]))
    return {"elevation_meters": meters, "elevation_feet": int(meters * 3.28084)}

def location_weather(loc):
    """Get the current weather for a lat/lon pair."""
    loc_str = str(loc["lat"]) + "," + str(loc["lon"])
    r = requests.get("https://wttr.in/" + loc_str + "?format=%C+%t")
    return str(r.text)

def location_sunlight(loc):
    """Get sunrise/sunset times for a lat/lon pair."""
    params = {"lat": loc["lat"], "lng": loc["lon"], "formatted": 1}
    r = requests.get("https://api.sunrise-sunset.org/json", params=params)
    sun = r.json()["results"]
    return {
        "sunrise": sun["sunrise"] + " GMT",
        "sunset": sun["sunset"] + " GMT",
        "solar_noon": sun["solar_noon"] + " GMT",
        "day_length": sun["day_length"] + " GMT",
    }

def get_zip_info(zipcode):
    """Aggregate location, elevation, weather, and sunlight for a zip code."""
    info = {"target_zipcode": str(zipcode)}
    try:
        loc = zipcode_location(zipcode)
        info["location"] = loc
    except Exception:
        info["location"] = "Zipcode not found."
        return info
    try:
        info["elevation"] = location_elevation(loc)
    except Exception:
        info["elevation"] = "Elevation data not found."
    try:
        info["weather"] = location_weather(loc)
    except Exception:
        info["weather"] = "Weather data not found."
    try:
        info["sunlight"] = location_sunlight(loc)
    except Exception:
        info["sunlight"] = "Sunlight data not found."
    return info
'''


# -- Deploy it -------------------------------------------------------------

result = deploy_agent(agent_code)
agent_id = result["api_id"]
print(f"Deployed!  Agent ID: {agent_id}")


# -- Call it ---------------------------------------------------------------

output = call_agent(agent_id, "get_zip_info", 78749)
print(json.dumps(output, indent=4))
