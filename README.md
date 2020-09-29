# Dash Earthquakes

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/jackdbd/dash-earthquakes.svg?branch=master)](https://travis-ci.org/jackdbd/dash-earthquakes) [![Python 3](https://pyup.io/repos/github/jackdbd/dash-earthquakes/python-3-shield.svg)](https://pyup.io/repos/github/jackdbd/dash-earthquakes/)

A Plotly Dash application showing earthquake data from the [US Geological Survey](https://earthquake.usgs.gov/).

The [GeoJSON summary feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) from the USGS website is updated every 15 minutes and it refers to the 4.5+ magnitude earthquakes occurred in the past month.

![A GIF file showing a short demo on how to use the Dash Earthquakes dashboard](https://github.com/jackdbd/dash-earthquakes/blob/master/demo.gif "How to use the Dash Earthquakes dashboard")

[App on Heroku](https://belle-croissant-54211.herokuapp.com/)

Built with:

- [Plotly Dash](https://plotly.com/dash/)
- [mapbox](https://www.mapbox.com/)
- [Font Awesome](http://fontawesome.io/)
- [jQuery Datatables](https://datatables.net/)

## API keys

This project requires to get some API keys from external services.

- `PLOTLY_USERNAME`, `PLOTLY_API_KEY`: get them at [chart-studio.plotly.com](https://chart-studio.plotly.com/).

## Installation

:warning: Do **NOT** use the `requirements.txt` file to install the dependencies on your machine. I need to keep it to deploy on Heroku because [Heroku does not yet support poetry](https://github.com/heroku/heroku-buildpack-python/issues/796) (I tried [this buildpack](https://elements.heroku.com/buildpacks/moneymeets/python-poetry-buildpack) but it didn't work).

This project uses [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to manage the Python virtual environment, and [poetry](https://poetry.eustace.io/) to manage the project dependencies.

If you don't have it, install python `3.8.5`.

```shell
pyenv install 3.8.5
```

Create a virtual environment and activate it.

```shell
pyenv virtualenv 3.8.5 dash_earthquakes
pyenv activate dash_earthquakes
```

Remember to activate the virtual environment every time you work on this project.

Install all the dependencies from the `poetry.lock` file.

```shell
poetry install
```

## Usage

This project uses the task runner [Poe the Poet](https://github.com/nat-n/poethepoet) to run poetry scripts.

Run the app locally using a development server (Dash uses a Flask development server):

```shell
poetry run poe dev

# or, in alternative
python app.py
```

Run the app locally using a production server (gunicorn):

```shell
poetry run poe prod
```

Run all tests with pytest:

```shell
poetry run poe test
```

Format all code with black:

```shell
poetry run poe format
```

## Docker

Build the Docker image and give it a name and a version tag:

```shell
docker build -t dash-earthquakes:v0.1.0 .
```

Run the Docker container:

```shell
docker run --env-file .env -p 5001:5000 dash-earthquakes:v0.1.0
```

Deploy the dockerized app on CapRover (running on my DigitalOcean Droplet):

```shell
./deploy.sh
```

## Troubleshooting

If you are on Ubuntu you might get `ModuleNotFoundError: No module named '_bz2'` and/or `UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError.` These errors are caused by pandas when it tries to import these [compression libraries](https://github.com/pandas-dev/pandas/issues/27575). If you get these errors you need to install the libbz2-dev package and the liblzma-dev package, then re-compile your python interpreter.

Here is how you can do it:

```shell
# deactivate and remove the virtual environment
pyenv deactivate
pyenv virtualenv-delete dash_earthquakes

# remove the "broken" python interpreter
pyenv uninstall 3.8.5

# install the compression libreries
sudo apt-get install libbz2-dev liblzma-dev

# download and compile the python interpreter
pyenv install 3.8.5

# re-create the virtual environment and activate it
pyenv virtualenv 3.8.5 dash_earthquakes
pyenv activate dash_earthquakes

# re-install all the dependencies
poetry install
```

Generate `requirements.txt` to deploy on Heroku:

```shell
poetry export -o requirements.txt
```
