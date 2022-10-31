import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import geopandas as gpd


#----------------------------------------------------------------------------------------------------------------------------


def empty_maps(df3_topcompanies):
    
    map_london = Map(location=[df3_topcompanies["latitude"].iloc[0], df3_topcompanies["longitude"].iloc[0]], zoom_start=15)
    map_newyork = Map(location=[df3_topcompanies["latitude"].iloc[1], df3_topcompanies["longitude"].iloc[1]], zoom_start=15)
    map_sanfrancisco = Map(location=[df3_topcompanies["latitude"].iloc[2], df3_topcompanies["longitude"].iloc[2]], zoom_start=15)
    
    return map_london, map_newyork, map_sanfrancisco
    
#----------------------------------------------------------------------------------------------------------------------------

def creating_maps(df_company, df, map_):
    
    headquarters = {"location": [df_company["latitude"], df_company["longitude"]], "tooltip": df_company["name"]}
    icon = Icon (
                color="blue",
                opacity = 0.6,
                prefix = "fa",
                icon="building-o",
                icon_color = "black"
            )
    new_marker = Marker(**headquarters, icon = icon, radius = 2)
    new_marker.add_to(map_)
    
    
    for index, row in df.iterrows():

        place = {"location": [row["lat"], row["lon"]], "tooltip": row["distance_from_company"]}

        if row["type_of_place"] == "Night Club":        
            icon = Icon (
                color="red",
                opacity = 0.6,
                prefix = "fa",
                icon="glass",
                icon_color = "white"
            )
            
        elif row["type_of_place"] == "Bar":
            icon = Icon (
                color="orange",
                opacity = 0.6,
                prefix = "fa",
                icon="beer",
                icon_color = "white"
            )
            
        elif row["type_of_place"] == "Nursery School":
            icon = Icon (
                color="white",
                opacity = 0.6,
                prefix = "fa",
                icon="minus-circle",
                icon_color = "black"
           )
        elif row["type_of_place"] == "Elementary School":
            icon = Icon (
                color="black",
                opacity = 0.6,
                prefix = "fa",
                icon="plus-circle",
                icon_color = "white"
            )
        else:
            icon = Icon (
                color="blue",
                opacity = 0.6,
                prefix = "fa",
                icon="plane",
                icon_color = "white",
            )
        new_marker = Marker(**place, icon = icon, radius = 2)

        new_marker.add_to(map_)
        
#----------------------------------------------------------------------------------------------------------------------------

