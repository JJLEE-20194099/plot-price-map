from dash import Dash, html
import os
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

data_list = json.load(open('./files/json/map/hn/refined_price_map_data_by_street.json', encoding='utf-8'))

lat_list = [data["input"]["LAT"] for data in data_list]
lon_list = [data["input"]["LNG"] for data in data_list]
street_price_list = [int(data["output"]["streetHousePrice"]["mean"]) for data in data_list]
text_list = [f'Alley Price: {str([int(data["output"]["alleyHousePrice"]["1"]["mean"]), int(data["output"]["alleyHousePrice"]["2"]["mean"]), int(data["output"]["alleyHousePrice"]["3"]["mean"])])}' for data in data_list]
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
meeyland_df = meeyland_df[meeyland_df['price'] <= 950]


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
ward_data = json.load(open('./files/json/map/hn/price_map_groupby_ward_with_mean_refine.json', encoding='utf-8'))
district_list = list(district_data.keys())
alley_1_price = [int(district_data[district]["alleyHousePrice"]["1"]["mean"]) for district in district_list]
alley_2_price = [int(district_data[district]["alleyHousePrice"]["2"]["mean"]) for district in district_list]
alley_3_price = [int(district_data[district]["alleyHousePrice"]["3"]["mean"]) for district in district_list]
street_price = [int(district_data[district]["streetHousePrice"]["mean"]) for district in district_list]

fig3 = go.Figure(data=[
    go.Bar(name='Street - House Pice', x=district_list, y=street_price),
    go.Bar(name='Alley 1 - House Price', x=district_list, y=alley_1_price),
    go.Bar(name='Alley 2 - House Price', x=district_list, y=alley_2_price),
    go.Bar(name='Alley 3 - House Price', x=district_list, y=alley_3_price)
])
fig3.update_layout(barmode='group')

fig4 = go.Figure()

app = Dash(name=__name__)
# app = Dash(name=__name__, requests_pathname_prefix="/plot_price_map/")


@app.callback(
    Output('district-indicators', 'figure'),
    [Input('district-dropdown', 'value')])

def display_demographic_statistics(selected_district):
    ward_data_by_district = ward_data[selected_district]


    ward_list = list(ward_data_by_district.keys())
    alley_1_price = [ward_data_by_district[ward]["alleyHousePrice"]["1"]["mean"] for ward in ward_list]
    alley_2_price = [ward_data_by_district[ward]["alleyHousePrice"]["2"]["mean"] for ward in ward_list]
    alley_3_price = [ward_data_by_district[ward]["alleyHousePrice"]["3"]["mean"] for ward in ward_list]
    street_price = [ward_data_by_district[ward]["streetHousePrice"]["mean"] for ward in ward_list]

    return {
            'data': [
                go.Bar(name='Street - House Pice', x=ward_list, y=street_price),
                go.Bar(name='Alley 1 - House Price', x=ward_list, y=alley_1_price),
                go.Bar(name='Alley 2 - House Price', x=ward_list, y=alley_2_price),
                go.Bar(name='Alley 3 - House Price', x=ward_list, y=alley_3_price)
            ]
    }

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
    ]),
    html.Div([
        html.Div([html.H1('House Price By Ward in A Specific District')], style={'textAlign': 'center'}),
        dcc.Dropdown(id='district-dropdown',
            options=[{'label': x, 'value': x}
                    for x in district_list],
                value=district_list[0],
                multi=False, clearable=True),
        dcc.Graph(id='district-indicators',  figure=fig4)
    ]),

])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9000)