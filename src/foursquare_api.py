from pymongo import MongoClient
import pandas as pd
import numpy as np
import time

import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd

import geopandas as gpd
from cartoframes.viz import Map, Layer, popup_element

import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import statistics as s

import haversine as hs
load_dotenv()

token_fsq = os.getenv("key")


#----------------------------------------------------------------------------------------------------------------------------

def get_results_from_foursquare (query, location, limit):

    ll = f"{location[1]}%2C{location[0]}"
    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={ll}&sort=DISTANCE&limit={str(limit)}"

    headers = {
        "accept": "application/json",
        "Authorization": token_fsq,
    }

    response = requests.get(url, headers=headers).json()
    
    return response

#----------------------------------------------------------------------------------------------------------------------------

def making_requests(query):
    
    location = []
    dict_of_dfs = dict()

    for index, row in df3_topcompanies.iterrows():

        location.append(row["longitude"])
        location.append(row["latitude"])

        places = get_results_from_foursquare(query, location, 50)
        print(places)

        dict_of_dfs[row["city"]] = creating_dfs(places, query, row["city"])

        location = []
               
    return dict_of_dfs

#----------------------------------------------------------------------------------------------------------------------------

def creating_dfs(res, type_of_place, city):
    
    new_list = []
    
    for i in res["results"]:
    
        name = i["name"]
        address =  i["location"]["formatted_address"]
        lat = i["geocodes"]["main"]["latitude"]
        lon = i["geocodes"]["main"]["longitude"]
        distance_from_company = i["distance"]

        type_ = {"typepoint": 
                              {"type": "Point", 
                               "coordinates": [lat, lon]}}

        new_list.append({"name":name, "lat":lat, "lon":lon, "city": city, "type":type_, "address": address, "type_of_place": type_of_place,           "distance_from_company": distance_from_company})
        
    df = pd.DataFrame.from_records(new_list)
        
    return df

#----------------------------------------------------------------------------------------------------------------------------

