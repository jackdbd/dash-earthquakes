# dash-earthquakes
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/jackdbd/dash-earthquakes.svg?branch=master)](https://travis-ci.org/jackdbd/dash-earthquakes) [![Python 3](https://pyup.io/repos/github/jackdbd/dash-earthquakes/python-3-shield.svg)](https://pyup.io/repos/github/jackdbd/dash-earthquakes/)

A Plotly Dash application showing earthquake data from the [US Geological Survey](https://earthquake.usgs.gov/)

The [GeoJSON summary feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) from the USGS website is updated every 15 minutes and it refers to the 4.5+ magnitude earthquakes occurred in the past month.

![A GIF file showing a short demo on how to use the Dash Earthquakes dashboard](https://github.com/jackdbd/dash-earthquakes/blob/master/demo.gif "How to use the Dash Earthquakes dashboard")

[App on Heroku](https://belle-croissant-54211.herokuapp.com/)

Built with:

- [Plotly Dash](https://plot.ly/products/dash/)
- [mapbox](https://www.mapbox.com/)
- [Font Awesome](http://fontawesome.io/)
- [jQuery Datatables](https://datatables.net/)
