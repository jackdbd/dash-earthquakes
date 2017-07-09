import os
import requests
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, json
from dash import Dash
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

usgs = 'http://earthquake.usgs.gov/earthquakes/'
geoJsonFeed = 'feed/v1.0/summary/4.5_month.geojson'
url = '{}{}'.format(usgs, geoJsonFeed)
req = requests.get(url)
d = json.loads(req.text)
print(d['metadata'])

app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = Dash(name=app_name, server=server, csrf_protect=False)

app.layout = html.Div(children=[
    html.H1(children=app_name),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
