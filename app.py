import os
# import requests
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import Flask, json
from dash import Dash
from dash.dependencies import Input, Output
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# usgs = 'http://earthquake.usgs.gov/earthquakes/'
# geoJsonFeed = 'feed/v1.0/summary/4.5_month.geojson'
# url = '{}{}'.format(usgs, geoJsonFeed)
# req = requests.get(url)
# data = json.loads(req.text)

mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN', 'mapbox-token')


# local development
with open('4.5_month.geojson') as data_file:
    data = json.load(data_file)


def create_dataframe(d):
    features = d['features']
    # earthquake properties: Place, Magnitude, Time, Timezone
    properties = [x['properties'] for x in features]
    # earthquake coordinates: Latitude, Longitude, Depth
    geometries = [x['geometry'] for x in features]
    coordinates = [x['coordinates'] for x in geometries]
    dd = {
        'Place': [x['place'] for x in properties],
        'Magnitude': [x['mag'] for x in properties],
        'Time': [x['time'] for x in properties],
        'Timezone': [x['tz'] for x in properties],
        'Longitude': [x[0] for x in coordinates],
        'Latitude': [x[1] for x in coordinates],
        'Depth': [x[2] for x in coordinates],
    }
    return pd.DataFrame(dd)

dataframe = create_dataframe(data)
# print(dataframe.head())
# print(data['metadata']['count'])


def create_table(df, max_rows=10):
    columns = df.columns.values
    num_rows = min(df.shape[0], max_rows)
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in columns])] +

        # Body
        [html.Tr([html.Td(df.iloc[i][col]) for col in columns])
         for i in range(num_rows)]
    )
    return table

styles = {
    'column': {
        'display': 'inline-block',
        # 'width': '33%',
        'padding': 10,
        'background-color': '#ff0000',
        'boxSizing': 'border-box',
        'minHeight': '200px'
    },
    'pre': {'border': 'thin lightgrey solid'}
}

app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = Dash(name=app_name, server=server, csrf_protect=False)

app.layout = html.Div(children=[
    html.H1(children=app_name),
    html.Div([
        create_table(dataframe),
    ], style=styles['column']),

    dcc.Dropdown(
        options=[
            {'label': 'San Francisco', 'value': 'SF'},
            {'label': 'Los Angeles', 'value': 'LA'},
        ],
        value='SF',
        id='my-dropdown'
    ),

    # create empty figure. It will be updated when _update_graph is triggered
    dcc.Graph(id='graph-geo'),
])

@app.callback(
    output=Output('graph-geo', 'figure'),
    inputs=[Input('my-dropdown', 'value')])
def _update_graph(val):
    dff = dataframe

    # Viareggio
    lat = 43.866667
    lon = 10.233333

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        height=750,
        # margin=go.Margin(l=50, r=20, t=10, b=80),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=lon
            ),
            pitch=0,
            zoom=8,
            # style="dark",
        ),
    )

    data = go.Data([
        go.Scattermapbox(
            lat=['{}'.format(lat)],
            lon=['{}'.format(lon)],
            mode='markers',
            marker=go.Marker(
                size=14
            ),
            text=['Viareggio'],
        )
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
