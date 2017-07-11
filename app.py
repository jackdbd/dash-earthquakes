import os
import arrow
# import requests
import functools
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

# http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=5
colorscale_magnitude = [
    [0, '#ffffb2'],
    [0.25, '#fecc5c'],
    [0.5, '#fd8d3c'],
    [0.75, '#f03b20'],
    [1, '#bd0026'],
]

# http://colorbrewer2.org/#type=sequential&scheme=Greys&n=3
colorscale_depth = [
    [0, '#f0f0f0'],
    [0.5, '#bdbdbd'],
    [0.1, '#636363'],
]


# local development
with open('4.5_month.geojson') as data_file:
    data = json.load(data_file)


def convert_timestamp(timestamp_ms):
    return arrow.get(timestamp_ms / 1000.0).format()


def create_dataframe(d):
    features = d['features']
    properties = [x['properties'] for x in features]
    geometries = [x['geometry'] for x in features]
    coordinates = [x['coordinates'] for x in geometries]
    times = [convert_timestamp(x['time']) for x in properties]
    dd = {
        'Place': [x['place'] for x in properties],
        'Magnitude': [x['mag'] for x in properties],
        'Time': times,
        # 'Timezone': [x['tz'] for x in properties],
        'Detail': [x['detail'] for x in properties],
        'Longitude': [x[0] for x in coordinates],
        'Latitude': [x[1] for x in coordinates],
        'Depth': [x[2] for x in coordinates],
    }
    # html text to display when hovering
    texts = list()
    for i in range(len(properties)):
        text = '{}<br>{}<br>Magnitude: {}<br>Depth: {} km'.format(
            dd['Time'][i], dd['Place'][i], dd['Magnitude'][i], dd['Depth'][i])
        texts.append(text)
    dd.update({'Text': texts})
    return pd.DataFrame(dd)


def create_metadata(d):
    dd = {
        'title': d['metadata']['title'],
        'api': d['metadata']['api'],
    }
    return dd

dataframe = create_dataframe(data)
metadata = create_metadata(data)
# print(dataframe.head())


def create_td(series, col):
    val = series[col]
    if col == 'Detail':
        td = html.Td(
            html.A(children='GeoJSON', href='{}'.format(val), target='_blank'))
    else:
        td = html.Td(val)
    return td


def create_table(df):
    columns = ['Magnitude', 'Latitude', 'Longitude', 'Time', 'Place', 'Detail']
    num_rows = data['metadata']['count']
    thead = html.Thead(html.Tr([html.Th(col) for col in columns]))
    table_rows = list()
    for i in range(num_rows):
        tr = html.Tr(
            children=list(map(functools.partial(create_td, df.iloc[i]),
                              columns)))
        table_rows.append(tr)
    tbody = html.Tbody(children=table_rows)
    table = html.Table(children=[thead, tbody], id='my-table')
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

regions = {
    'world': {'lat': 0, 'lon': 0, 'zoom': 1},
    'europe': {'lat': 50, 'lon': 0, 'zoom': 3},
    'north_america': {'lat': 40, 'lon': -100, 'zoom': 2},
    'south_america': {'lat': -15, 'lon': -60, 'zoom': 2},
    'africa': {'lat': 0, 'lon': 20, 'zoom': 2},
    'asia': {'lat': 30, 'lon': 100, 'zoom': 2},
    'oceania': {'lat': -10, 'lon': 130, 'zoom': 2},
}

app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = Dash(name=app_name, server=server, csrf_protect=False)

app.layout = html.Div(children=[
    html.H1(children=app_name, style={'font-family': 'Raleway'}),

    html.A(
        children=[html.I(children=[], className='fa fa-twitter fa-2x')],
        id='tweet', title='Tweet me!', href='https://twitter.com/',
        target='_blank',
    ),

    html.I(children=[], className='fa fa-github fa-2x'),

    html.Label('Map style'),
    dcc.Dropdown(
        options=[
            {'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
        ],
        value='dark',
        id='dropdown-map-style'
    ),

    html.Label('Region'),
    dcc.Dropdown(
        options=[
            {'label': 'World', 'value': 'world'},
            {'label': 'Europe', 'value': 'europe'},
            {'label': 'North America', 'value': 'north_america'},
            {'label': 'South America', 'value': 'south_america'},
            {'label': 'Africa', 'value': 'africa'},
            {'label': 'Asia', 'value': 'asia'},
            {'label': 'Oceania', 'value': 'oceania'},
        ],
        value='world',
        id='dropdown-region'
    ),

    # create empty figure. It will be updated when _update_graph is triggered
    dcc.Graph(id='graph-geo'),

    html.Div(
        children=[create_table(dataframe)],
        style={
            'font-family': 'Raleway',
            'padding-left': '6%',
            'padding-right': '6%'}
    ),
])


@app.callback(
    output=Output('graph-geo', 'figure'),
    inputs=[Input('dropdown-map-style', 'value'),
            Input('dropdown-region', 'value')])
def _update_graph(map_style, region):
    dff = dataframe
    radius_multiplier = {'inner': 1.5, 'outer': 3}

    layout = go.Layout(
        title=metadata['title'],
        autosize=True,
        hovermode='closest',
        height=750,
        font=dict(family='Raleway'),
        # margin=go.Margin(l=50, r=20, t=10, b=80),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=regions[region]['lat'],
                lon=regions[region]['lon'],
            ),
            pitch=0,
            zoom=regions[region]['zoom'],
            style=map_style,
        ),
    )

    data = go.Data([
        # outer circles represent magnitude
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.Marker(
                size=dff['Magnitude'] * radius_multiplier['outer'],
                colorscale=colorscale_magnitude,
                color=dff['Magnitude'],
                opacity=1,
            ),
            text=dff['Text'],
            # hoverinfo='text',
            showlegend=False,
        ),
        # inner circles represent depth
        go.Scattermapbox(
            lat=dff['Latitude'],
            lon=dff['Longitude'],
            mode='markers',
            marker=go.Marker(
                size=dff['Magnitude'] * radius_multiplier['inner'],
                colorscale=colorscale_depth,
                color=dff['Depth'],
                opacity=1,
            ),
            hoverinfo='skip',  # outer circles already handle hovering
            showlegend=False
        ),
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure

external_js = [
    # google analytics
    'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/'
    'e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js',
    # jQuery, DataTables, script to initialize DataTables
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://codepen.io/jackaljack/pen/bROVgV.js',
]

for js in external_js:
    app.scripts.append_script({'external_url': js})

external_css = [
    'https://fonts.googleapis.com/css?family=Raleway',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

for css in external_css:
    app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
