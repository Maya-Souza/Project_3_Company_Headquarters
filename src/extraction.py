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

#------------------------------------------------------------------------------------------------------------------------

#connecting to Mongo database

client = MongoClient("localhost:27017")
db = client["ironhack"]
c = db.get_collection("companies")

#------------------------------------------------------------------------------------------------------------------------

def filtering_companies():
    
    '''
    Filtering companies based on the criteria explained in the README

    '''

    condition1 = {"total_money_raised" : {"$regex": "\d{2,}\.?\d?M|\d{1,}\.?\d?B"}}
    condition2 = {"tag_list": {"$regex": ".*design.|.tech.|.software.|.fashion."}}
    condition3 = {"category_code": "web"}
    condition4 = {"offices": {"$ne": []}}

    projection = {"_id": 0, "name":1, "offices.city":1, "offices.latitude":1, "offices.longitude": 1, "address1":1, "total_money_raised": 1}

    query = {"$and": [condition1, condition4, {"$or": [condition2, condition3]}]}


    filtered_companies = list(c.find(query, projection))
    df = pd.DataFrame(filtered_companies)
    
    return df

#------------------------------------------------------------------------------------------------------------------------


def cleaning_companies_df(df):
    
    '''
    Standardizing the companies dataframes by getting only the info that is relevant to my analysis
    and tranforming the money_raised column into floats.
    I realize that by disregarding the currency type, the numerical values are not precise. However,
    since I don't need precise values here, it doesn't matter.
    
    '''

    df = df.explode("offices")
    df.reset_index(drop=True)
    
    cities = []
    latitudes = []
    longitudes = []
    addresses = []
    money = []

    for index, row in df.iterrows():

        try:
            cities.append(row["offices"]["city"])
            latitudes.append(row["offices"]["latitude"])
            longitudes.append(row["offices"]["longitude"])

        except IndexError:
            cities.append(None)
            latitudes.append(None)
            longitudes.append(None)


    df["city"] = cities
    df["latitude"] = latitudes
    df["longitude"] = longitudes
    
    df = df.drop("offices", axis=1)
    
    df["total_money_raised"] = df["total_money_raised"].replace('M|\$|€|C|£', "", regex = True).replace('B', "000", regex = True)
    df["total_money_raised"] = pd.to_numeric(df["total_money_raised"])

    df.to_csv("filtered_companies.csv", index=False)
    
    return df

#------------------------------------------------------------------------------------------------------------------------

def creating_airports_df(airports, city):
    
    type_ = []

    new = airports.loc[(airports["municipality"] == city) & (~airports["type"].isin(["closed", "seaplane_base", "heliport"]))]
    
    new = new.filter(['name','latitude_deg','longitude_deg', 'municipality'], axis=1).reset_index(drop=True)
    
    new.rename(columns = {'latitude_deg': 'lat', 'longitude_deg': 'lon', 'municipality':'city'}, inplace=True)
    
    for index, row in new.iterrows():
        type_.append({"typepoint": {"type": "Point", "coordinates": [row["lat"], row["lon"]]}})
        
    new['type'] = pd.Series(type_)
    new['address'] = None
    new['type_of_place'] = 'Airport'
    new['distance_from_company'] = 0

    return new

#------------------------------------------------------------------------------------------------------------------------

def distances_airports(coord_company, df):
    
    distance_from_company = []
    
    for i in range(df.shape[0]):    
        
        distance_from_company.append(hs.haversine((df["lat"].iloc[i], df["lon"].iloc[i]), (coord_company)))

    df["distance_from_company"] = pd.Series(distance_from_company)
    
    
#------------------------------------------------------------------------------------------------------------------------

    