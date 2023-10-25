from dash import Dash, html
import os
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
from dash import Dash, html, dcc, Input, Output, Patch, clientside_callback, callback
import plotly.io as pio
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

load_figure_template(["minty", "minty_dark"])

data = json.load(open('./files/json/map/hn/refined_price_map_data_by_street.json', encoding='utf-8'))
data_list = []
for _, val in data.items():
    data_list = data_list + val

lat_list = [data["lat"] for data in data_list]
lon_list = [data["lon"] for data in data_list]
street_price_list = [int(data["estimatePrice"]["output"]["streetHousePrice"]["mean"]) for data in data_list]
text_list = [f'Alley Price: {str([int(data["estimatePrice"]["output"]["alleyHousePrice"]["1"]["mean"]), int(data["estimatePrice"]["output"]["alleyHousePrice"]["2"]["mean"]), int(data["estimatePrice"]["output"]["alleyHousePrice"]["3"]["mean"])])}' for data in data_list]
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
                                zoom=8, size = "street_price", size_max=20, opacity=1)
fig1.update_layout(mapbox_style="open-street-map")
fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



color_scale = [(0, 'orange'), (1,'red')]

fig2 = px.scatter_mapbox(meeyland_df, lat='lat', lon="lon", color="price", color_continuous_scale=[[0, 'green'], [0.5, 'red'], [1.0, 'rgb(0, 0, 255)']],
                                zoom=8, size = "price", size_max=20, opacity=1)
fig2.update_layout(mapbox_style="open-street-map")
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


district_data = data.copy()
district_list = list(district_data.keys())
alley_1_price = [np.mean(np.array([int(item["estimatePrice"]["output"]["alleyHousePrice"]["1"]["mean"]) for item in district_data[district]])) for district in district_list]
alley_2_price = [np.mean(np.array([int(item["estimatePrice"]["output"]["alleyHousePrice"]["2"]["mean"]) for item in district_data[district]])) for district in district_list]
alley_3_price = [np.mean(np.array([int(item["estimatePrice"]["output"]["alleyHousePrice"]["3"]["mean"]) for item in district_data[district]])) for district in district_list]
street_price = [np.mean(np.array([int(item["estimatePrice"]["output"]["streetHousePrice"]["mean"]) for item in district_data[district]])) for district in district_list]

fig3 = go.Figure(data=[
    go.Bar(name='Street - House Pice', x=district_list, y=street_price),
    go.Bar(name='Alley 1 - House Price', x=district_list, y=alley_1_price),
    go.Bar(name='Alley 2 - House Price', x=district_list, y=alley_2_price),
    go.Bar(name='Alley 3 - House Price', x=district_list, y=alley_3_price)
])
fig3.update_layout(barmode='group')

fig4 = go.Figure()
fig5 = go.Figure()
fig6 = go.Figure()


app = Dash(name=__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME])
# app = Dash(name=__name__, requests_pathname_prefix="/plot_price_map/")

color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch( id="color-mode-switch", value=False, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
)

ward_data = dict()
for district, streets in district_data.items():
    ward_by_district = dict()
    for street in streets:
        if street["ward"] not in ward_by_district.keys():
            ward_by_district[street["ward"]] = []

        ward_by_district[street["ward"]].append(street)
    ward_data[district] = ward_by_district

@app.callback(
    Output('district-indicators', 'figure'),
    [Input('district-dropdown', 'value')])

def display_demographic_statistics(selected_district):
    ward_data_by_district = ward_data[selected_district]


    ward_list = list(ward_data_by_district.keys())
    alley_1_price = [np.mean(np.array([item["estimatePrice"]["output"]["alleyHousePrice"]["1"]["mean"] for item in ward_data_by_district[ward]])) for ward in ward_list]
    alley_2_price = [np.mean(np.array([item["estimatePrice"]["output"]["alleyHousePrice"]["2"]["mean"] for item in ward_data_by_district[ward]])) for ward in ward_list]
    alley_3_price = [np.mean(np.array([item["estimatePrice"]["output"]["alleyHousePrice"]["3"]["mean"] for item in ward_data_by_district[ward]])) for ward in ward_list]
    street_price = [np.mean(np.array([item["estimatePrice"]["output"]["streetHousePrice"]["mean"] for item in ward_data_by_district[ward]])) for ward in ward_list]

    return {
            'data': [
                go.Bar(name='Street - House Price', x=ward_list, y=street_price),
                go.Bar(name='Alley 1 - House Price', x=ward_list, y=alley_1_price),
                go.Bar(name='Alley 2 - House Price', x=ward_list, y=alley_2_price),
                go.Bar(name='Alley 3 - House Price', x=ward_list, y=alley_3_price)
            ]
    }

@callback(
    Output("graph", "figure"),
    Input("color-mode-switch", "value"),
)
def update_figure_template(switch_on):
    template = pio.templates["minty"] if switch_on else pio.templates["minty_dark"]

    patched_figure = Patch()
    patched_figure["layout"]["template"] = template
    return patched_figure

clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

@app.callback(
    Output('district-indicators-distribution-1', 'figure'),
    [Input('district-dropdown-distribution-1', 'value')])

def display_demographic_distribution(selected_district):

    street_by_district = district_data[selected_district]
    fig = make_subplots(rows=2, cols=2)

    trace0 = go.Histogram(name='Alley 1 - House Price', x=[street["estimatePrice"]["output"]["alleyHousePrice"]["1"]["mean"] for street in street_by_district])
    trace1 = go.Histogram(name='Alley 2 - House Price',x=[street["estimatePrice"]["output"]["alleyHousePrice"]["2"]["mean"] for street in street_by_district])
    trace2 = go.Histogram(name='Alley 3 - House Price',x=[street["estimatePrice"]["output"]["alleyHousePrice"]["3"]["mean"] for street in street_by_district])
    trace3 = go.Histogram(name='Street - House Price',x=[street["estimatePrice"]["output"]["streetHousePrice"]["mean"] for street in street_by_district])
    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 1, 2)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 2, 2)

    return fig

@app.callback(
    Output('district-indicators-distribution-2', 'figure'),
    [Input('district-dropdown-distribution-2', 'value')])

def display_demographic_distribution(selected_district):

    street_by_district = district_data[selected_district]
    fig = make_subplots(rows=2, cols=2)

    trace0 = go.Histogram(name='Alley 1 - House Price', x=[street["estimatePrice"]["output"]["alleyHousePrice"]["1"]["mean"] for street in street_by_district])
    trace1 = go.Histogram(name='Alley 2 - House Price',x=[street["estimatePrice"]["output"]["alleyHousePrice"]["2"]["mean"] for street in street_by_district])
    trace2 = go.Histogram(name='Alley 3 - House Price',x=[street["estimatePrice"]["output"]["alleyHousePrice"]["3"]["mean"] for street in street_by_district])
    trace3 = go.Histogram(name='Street - House Price',x=[street["estimatePrice"]["output"]["streetHousePrice"]["mean"] for street in street_by_district])
    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 1, 2)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 2, 2)

    return fig




app.layout = html.Div([
    color_mode_switch,
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

    html.Div([html.H1('Price Distribution')], style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            dcc.Dropdown(id='district-dropdown-distribution-1',
            options=[{'label': x, 'value': x}
                    for x in district_list],
                value=district_list[0],
                multi=False, clearable=True),
            dcc.Graph(id='district-indicators-distribution-1',  figure=fig5)
        ], style={"flex": 1, "margin-right": 12}),

        html.Div([
            dcc.Dropdown(id='district-dropdown-distribution-2',
            options=[{'label': x, 'value': x}
                    for x in district_list],
                value=district_list[1],
                multi=False, clearable=True),
            dcc.Graph(id='district-indicators-distribution-2',  figure=fig6)
        ], style={"flex": 1, "margin-left": 12})
    ], style={"display":"flex", "justify-content": "space-between"}),
], style={'margin-left': 20, 'margin-right': 20})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9000)