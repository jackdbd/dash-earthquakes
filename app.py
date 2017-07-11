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


def create_dataframe(d):
    features = d['features']
    properties = [x['properties'] for x in features]
    geometries = [x['geometry'] for x in features]
    coordinates = [x['coordinates'] for x in geometries]
    dd = {
        'Place': [x['place'] for x in properties],
        'Magnitude': [x['mag'] for x in properties],
        'Time': [x['time'] for x in properties],
        'Timezone': [x['tz'] for x in properties],
        'Detail': [x['detail'] for x in properties],
        'Longitude': [x[0] for x in coordinates],
        'Latitude': [x[1] for x in coordinates],
        'Depth': [x[2] for x in coordinates],
    }
    # html text to display when hovering
    texts = list()
    for i in range(len(properties)):
        text = '{}<br>Magnitude: {}<br>Depth: {} km'\
            .format(dd['Place'][i], dd['Magnitude'][i], dd['Depth'][i])
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
# print(data['metadata']['count'])


def create_table(df, max_rows=1000):
    # columns = list(filter(lambda x: x != 'Text', df.columns.values))
    columns = ['Magnitude', 'Latitude', 'Longitude', 'Place', 'Time']
    num_rows = min(df.shape[0], max_rows)
    thead = html.Thead(html.Tr([html.Th(col) for col in columns]))
    table_rows = list()
    for i in range(num_rows):
        tr = html.Tr([html.Td(df.iloc[i][col]) for col in columns])
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
    inputs=[Input('my-dropdown', 'value')])
def _update_graph(val):
    dff = dataframe
    initial_latitude = 0
    initial_longitude = 0
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
                lat=initial_latitude,
                lon=initial_longitude
            ),
            pitch=0,
            zoom=1,
            style='dark',
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
    'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js',
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://codepen.io/jackaljack/pen/bROVgV.js',
]

for js in external_js:
    app.scripts.append_script({'external_url': js})

external_css = [
    'https://fonts.googleapis.com/css?family=Raleway',
    'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

for css in external_css:
    app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
