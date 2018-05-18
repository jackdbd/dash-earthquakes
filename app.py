import os
import arrow
import requests
import functools
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly as py
from flask import Flask, json
from dash import Dash
from dash.dependencies import Input, Output
from dotenv import load_dotenv

external_js = [
    # jQuery, DataTables, script to initialize DataTables
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://codepen.io/jackdbd/pen/bROVgV.js',
]

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    # 'https://fonts.googleapis.com/css?family=Lobster',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]


try:
    # the app is on Heroku
    os.environ['DYNO']
    debug = False
    # google analytics with my tracking ID
    # external_js.append('https://codepen.io/jackdbd/pen/NgmpzR.js')
except KeyError:
    debug = True
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

usgs = 'http://earthquake.usgs.gov/earthquakes/'
geoJsonFeed = 'feed/v1.0/summary/4.5_month.geojson'
url = '{}{}'.format(usgs, geoJsonFeed)
req = requests.get(url)
data = json.loads(req.text)

# local development
# with open('4.5_month.geojson') as data_file:
#     data = json.load(data_file)

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


theme = {
    'font-family': 'Raleway',
    'background-color': '#787878',
}


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


def create_header(some_string):
    header_style = {
        'background-color': theme['background-color'],
        'padding': '1.5rem',
    }
    header = html.Header(html.H1(children=some_string, style=header_style))
    return header


def create_footer():
    p = html.P(
        children=[
            html.Span('Built with '),
            html.A('Plotly Dash',
                   href='https://github.com/plotly/dash', target='_blank'),
            html.Span(' and:'),
        ],
    )

    span_style = {'vertical-align': 'top', 'padding-left': '1rem'}

    usgs = html.A(
        children=[
            html.I([], className='fa fa-list fa-2x'),
            html.Span('USGS GeoJSON feed', style=span_style)
        ], style={'text-decoration': 'none'},
        href='https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php',
        target='_blank')
    mapbox = html.A(
        children=[
            html.I([], className='fa fa-map-o fa-2x'),
            html.Span('mapbox', style=span_style)
        ], style={'text-decoration': 'none'},
        href='https://www.mapbox.com/', target='_blank')

    font_awesome = html.A(
        children=[
            html.I([], className='fa fa-font-awesome fa-2x'),
            html.Span('Font Awesome', style=span_style)
        ], style={'text-decoration': 'none'},
        href='http://fontawesome.io/', target='_blank')
    datatables = html.A(
        children=[
            html.I([], className='fa fa-table fa-2x'),
            html.Span('jQuery Datatables', style=span_style)
        ], style={'text-decoration': 'none'},
        href='https://datatables.net/', target='_blank')

    ul1 = html.Ul(
        children=[
            html.Li(mapbox),
            html.Li(font_awesome),
            html.Li(datatables),
            html.Li(usgs),
        ],
        style={'list-style-type': 'none'},
    )

    hashtags = 'plotly,dash,usgs'
    tweet = 'Dash Earthquake, a cool dashboard with Plotly Dash!'
    twitter_href = 'https://twitter.com/intent/tweet?hashtags={}&text={}'\
        .format(hashtags, tweet)
    twitter = html.A(
        children=html.I(children=[], className='fa fa-twitter fa-3x'),
        title='Tweet me!', href=twitter_href, target='_blank')

    github = html.A(
        children=html.I(children=[], className='fa fa-github fa-3x'),
        title='Repo on GitHub',
        href='https://github.com/jackdbd/dash-earthquakes', target='_blank')

    li_right_first = {'line-style-type': 'none', 'display': 'inline-block'}
    li_right_others = {k: v for k, v in li_right_first.items()}
    li_right_others.update({'margin-left': '10px'})
    ul2 = html.Ul(
        children=[
            html.Li(twitter, style=li_right_first),
            html.Li(github, style=li_right_others),
        ],
        style={
            'position': 'absolute',
            'right': '1.5rem',
            'bottom': '1.5rem',
        }
    )

    div = html.Div([p, ul1, ul2])
    footer_style = {
        'font-size': '2.2rem',
        'background-color': theme['background-color'],
        'padding': '2.5rem',
        'margin-top': '3rem',
    }
    footer = html.Footer(div, style=footer_style)
    return footer


def create_dropdowns():
    drop1 = dcc.Dropdown(
        options=[
            {'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Satellite', 'value': 'satellite'},
            {
                'label': 'Custom',
                'value': 'mapbox://styles/jackdbd/cj6nva4oi14542rqr3djx1liz'
            }
        ],
        value='dark',
        id='dropdown-map-style',
        className='three columns offset-by-one'
    )
    drop2 = dcc.Dropdown(
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
        id='dropdown-region',
        className='three columns offset-by-four'
    )
    return [drop1, drop2]


def create_description():
    div = html.Div(
        children=[
            dcc.Markdown('''
            The redder the outer circle, the higher the magnitude. The darker 
            the inner circle, the deeper the earthquake.
                        
            > Currently no organization or government or scientist is capable 
            > of succesfully predicting the time and occurrence of an
            > earthquake.
            > — Michael Blanpied
            
            Use the table below to know more about the {} earthquakes that 
            exceeded magnitude 4.5 last month.

            ***
            '''.format(data['metadata']['count']).replace('  ', '')),
        ],
    )
    return div


def create_content():
    # create empty figure. It will be updated when _update_graph is triggered
    graph = dcc.Graph(id='graph-geo')
    content = html.Div(graph, id='content')
    return content

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
app = Dash(name=app_name, server=server)

app.layout = html.Div(
    children=[
        create_header(app_name),
        html.Div(
            children=[
                html.Div(create_dropdowns(), className='row'),
                html.Div(create_content(), className='row'),
                html.Div(create_description(), className='row'),
                html.Div(create_table(dataframe), className='row'),
            ],
        ),
        # html.Hr(),
        create_footer(),
    ],
    className='container',
    style={'font-family': theme['font-family']}
)

for js in external_js:
    app.scripts.append_script({'external_url': js})

for css in external_css:
    app.css.append_css({'external_url': css})


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
        font=dict(family=theme['font-family']),
        margin=go.Margin(l=0, r=0, t=45, b=10),
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
            # hovering behavior is already handled by outer circles
            hoverinfo='skip',
            showlegend=False
        ),
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=debug,  port=port, threaded=True)
