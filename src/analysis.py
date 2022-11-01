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
    
    '''
    Function that receives a list of dictionaries where each dictionary has 3 dataframes as values.
    The dictionaries are divided by place (e.g: bars, schools, etc) and not by city. This function creates 3 dataframes, one for each city, 
    by separating the ones inside the dictionaries and concatenating them in the right place.
    '''
    
    df1 = pd.DataFrame()
    
    for dic in list_:

        for df in dic.values():                

            if df["city"].iloc[0] == city:
                df1 = pd.concat([df1, df], axis=0).reset_index(drop = True)

    return df1

#----------------------------------------------------------------------------------------------------------------------------

def city_weights(df):
    
    '''
    Function that assigns weight to each type of place according to the description in the README. For bars and nightclubs it takes 
    into consideration the average of the 10 closest ones (since only one bar is not representative of "variety"). 
    For schools, 2 were taken, and for airports, only the closest one.
    '''
    
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
    
    '''
    Function that compares the weights given to each place and decides which city has the most variety of places closest to the building.
    '''
    
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
