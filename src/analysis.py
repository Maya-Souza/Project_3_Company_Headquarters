from pymongo import MongoClient
import numpy as np
import time

import os
import requests
import json
from dotenv import load_dotenv

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

def concat_dfs(list_, city):
    
    df1 = pd.DataFrame()
    
    for dic in list_:

        for df in dic.values():                

            if df["city"].iloc[0] == city:
                df1 = pd.concat([df1, df], axis=0).reset_index(drop = True)

    return df1

#----------------------------------------------------------------------------------------------------------------------------

def city_weights(df):
    
    city = df["city"].iloc[0] 
    weights = {"bars" : round((df.loc[df["type_of_place"] == "Bar"]["distance_from_company"].head(10).mean())*0.6, 2),
                "nightclubs" : round((df.loc[df["type_of_place"] == "Night Club"]["distance_from_company"].head(10).mean())*0.6, 2),
                "elementary_schools": round(df.loc[df["type_of_place"] == "Elementary School"]["distance_from_company"].head(2).mean()*0.9, 2),
                "nurseries": round(df.loc[df["type_of_place"] == "Nursery School"]["distance_from_company"].head(2).mean()*0.8, 1),
                "airports": round(df.loc[df["type_of_place"] == "Airport"]["distance_from_company"].min(), 1),
                'city' : city
}
    return weights

#----------------------------------------------------------------------------------------------------------------------------

def city_score(city_weight1, city_weight2, city_weight3):
    
    keys_from_cityweight = list(city_weight1.keys())
    score = []
    
    for i in range(len(city_weight1)):
            
        if (city_weight1[keys_from_cityweight[i]] < city_weight2[keys_from_cityweight[i]]) & (city_weight1[keys_from_cityweight[i]] <                     city_weight3[keys_from_cityweight[i]]):
            score.append(city_weight1['city'])
            
        elif (city_weight2[keys_from_cityweight[i]] < city_weight1[keys_from_cityweight[i]]) & (city_weight2[keys_from_cityweight[i]] <                    city_weight3[keys_from_cityweight[i]]):
             score.append(city_weight2['city'])
        
        elif (city_weight3[keys_from_cityweight[i]] < city_weight2[keys_from_cityweight[i]]) & (city_weight3[keys_from_cityweight[i]] <                    city_weight1[keys_from_cityweight[i]]):
             score.append(city_weight3['city'])
    
    return f"The best city for the HQ is {s.multimode(score)}"

#----------------------------------------------------------------------------------------------------------------------------
