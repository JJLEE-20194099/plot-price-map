from dash import Dash, html
import os
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px

data_list = json.load(open('./files/json/map/hn/refined_price_map_data_by_street.json', encoding='utf-8'))

lat_list = [data["input"]["LAT"] for data in data_list]
lon_list = [data["input"]["LNG"] for data in data_list]
street_price_list = [data["output"]["streetHousePrice"]["mean"] for data in data_list]
text_list = [f'Alley Price: {str([data["output"]["alleyHousePrice"]["1"]["mean"], data["output"]["alleyHousePrice"]["2"]["mean"], data["output"]["alleyHousePrice"]["3"]["mean"]])}' for data in data_list]
location_df = pd.DataFrame()
location_df['lat'] = lat_list
location_df['lon'] = lon_list
location_df['alley_price'] = text_list
location_df['street_price'] = street_price_list
location_df = location_df.reset_index().rename(columns = {'index': 'street_idx'})
location_df['lon'] = location_df['lon'].astype(np.float32)
location_df['lat'] = location_df['lat'].astype(np.float32)


meeyland_df = pd.read_csv('private_house_meey_land_location.csv')
meeyland_df = meeyland_df.groupby(['lat', 'lon'])['street_price'].mean().reset_index()
meeyland_df = meeyland_df.rename(columns={'street_price': 'price'})


color_scale = [(0, 'orange'), (1,'red')]

fig1 = px.scatter_mapbox(location_df, lat='lat', lon="lon", text = location_df['alley_price'].to_numpy(), color="street_price", color_continuous_scale=[[0, 'green'], [0.5, 'red'], [1.0, 'rgb(0, 0, 255)']],
                                zoom=8, size_max=10, opacity=1)
fig1.update_layout(mapbox_style="open-street-map")
fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



color_scale = [(0, 'orange'), (1,'red')]

fig2 = px.scatter_mapbox(meeyland_df, lat='lat', lon="lon", color="price", color_continuous_scale=[[0, 'green'], [0.5, 'red'], [1.0, 'rgb(0, 0, 255)']],
                                zoom=8, size_max=10, opacity=1)
fig2.update_layout(mapbox_style="open-street-map")
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


district_data = json.load(open('./files/json/map/hn/price_map_groupby_district_with_mean_refine.json', encoding='utf-8'))
district_list = list(district_data.keys())
alley_1_price = [district_data[district]["alleyHousePrice"]["1"]["mean"] for district in district_list]
alley_2_price = [district_data[district]["alleyHousePrice"]["2"]["mean"] for district in district_list]
alley_3_price = [district_data[district]["alleyHousePrice"]["3"]["mean"] for district in district_list]
street_price = [district_data[district]["streetHousePrice"]["mean"] for district in district_list]

fig3 = go.Figure(data=[
    go.Bar(name='Street - House Pice', x=district_list, y=street_price),
    go.Bar(name='Alley 1 - House Price', x=district_list, y=alley_1_price),
    go.Bar(name='Alley 2 - House Price', x=district_list, y=alley_2_price),
    go.Bar(name='Alley 3 - House Price', x=district_list, y=alley_3_price)
])
fig3.update_layout(barmode='group')



app = Dash(__name__)

app.layout = html.Div([
    html.Div([html.H1('Price Dashboard')], style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div([html.H1('Ha Noi - NestStock Price Map')], style={'textAlign': 'center'}),
            dcc.Graph(figure=fig1)
        ], style={"flex": 1, "margin-right": 12}),

        html.Div([
            html.Div([html.H1('Ha Noi - MeeyMap Price Map')], style={'textAlign': 'center'}),
            dcc.Graph(figure=fig2)
        ], style={"flex": 1, "margin-left": 12})
    ], style={"display":"flex", "justify-content": "space-between"}),
    html.Div([
        html.Div([html.H1('House Price By District')], style={'textAlign': 'center'}),
        dcc.Graph(figure=fig3)
    ])
])

if __name__ == '__main__':
    app.run(debug=True)