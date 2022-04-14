# Dash Earthquakes

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![CI](https://github.com/jackdbd/dash-earthquakes/actions/workflows/ci.yaml/badge.svg)](https://github.com/jackdbd/dash-earthquakes/actions/workflows/ci.yaml)

A Plotly Dash application showing earthquake data from the [US Geological Survey](https://earthquake.usgs.gov/).

The [GeoJSON summary feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) from the USGS website is updated every 15 minutes and it refers to the 4.5+ magnitude earthquakes occurred in the past month.

![A GIF file showing a short demo on how to use the Dash Earthquakes application](https://github.com/jackdbd/dash-earthquakes/blob/main/demo.gif "How to use Dash Earthquakes")

[App on Cloud Run](https://dash-earthquakes-production-45eyyotfta-ey.a.run.app).

Built with:

- [Plotly Dash](https://github.com/plotly/dash)
- [Mapbox](https://www.mapbox.com/)
- [Font Awesome](http://fontawesome.io/)
- [jQuery Datatables](https://datatables.net/)

## Environment variables

This project requires the following environment variables:

- `MAPBOX_ACCESS_TOKEN`: see [here](https://docs.mapbox.com/help/getting-started/access-tokens/) how to get one. You will find it on your [Mapbox account page](https://account.mapbox.com/);
- `PLOTLY_USERNAME` and `PLOTLY_API_KEY`: get them at [chart-studio.plotly.com](https://chart-studio.plotly.com/). You will find them on your [Plotly account settings page](https://chart-studio.plotly.com/settings/api).

I define all required environment variables in a `.envrc` file, so [direnv](https://github.com/direnv/direnv) picks them automatically.

## Installation

This project uses [pyenv](https://github.com/pyenv/pyenv) to specify the Python interpreter, [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to manage the Python virtual environment, and [poetry](https://poetry.eustace.io/) to manage the project's dependencies.

If you don't already have it, install python `3.8.5` using pyenv:

```shell
pyenv install 3.8.5
```

Create a virtual environment for this project, then activate it:

```shell
pyenv virtualenv 3.8.5 dash_earthquakes
```

Every time you work on this project, remember to activate the virtual environment:

```sh
pyenv activate dash_earthquakes

# and when you stop working on this project, run:
pyenv deactivate
```

Install all the dependencies from the `poetry.lock` file.

```shell
poetry install
```

## Tasks

This project uses the task runner [Poe the Poet](https://github.com/nat-n/poethepoet) to run poetry scripts.

## Development

Run the app locally using a development server (Dash uses a Flask development server):

```shell
poetry run poe dev
```

Run all tests with pytest:

```shell
poetry run poe test
```

Format all code with black:

```shell
poetry run poe format
```

## Build

Build the container image using the `Dockerfile`:

```sh
poetry run poe container_build
```

Create a container and run it:

```sh
poetry run poe container_run
```

## Deployment

Trigger a build on [Cloud Build](https://cloud.google.com/build). Cloud Build will build a container image, push it to [Artifact Registry](https://cloud.google.com/artifact-registry), then deploy the app to [Cloud Run](https://cloud.google.com/run):

```sh
gcloud builds submit ./ \
  --config cloudbuild.yaml \
  --project $GCP_PROJECT_ID \
  --substitutions _MAPBOX_ACCESS_TOKEN=$MAPBOX_ACCESS_TOKEN,_PLOTLY_API_KEY=$PLOTLY_API_KEY,_PLOTLY_USERNAME=$PLOTLY_USERNAME \
  --async
```

## Troubleshooting

Run a vulnerability scan with [trivy](https://github.com/aquasecurity/trivy) (you will need to install it):

```sh
poetry run poe container_scan
```

Explore the container image with [dive](https://github.com/wagoodman/dive) (you will need to install it):

```sh
poetry run poe container_explore
```

If you are on Ubuntu you might get `ModuleNotFoundError: No module named '_bz2'` and/or `UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError.` These errors are caused by pandas when it tries to import these [compression libraries](https://github.com/pandas-dev/pandas/issues/27575). If you get these errors you need to install the libbz2-dev package and the liblzma-dev package, then re-compile your python interpreter.

Here is how you can do it:

```shell
# deactivate and remove the virtual environment
pyenv deactivate
pyenv virtualenv-delete dash_earthquakes

# remove the "broken" python interpreter
pyenv uninstall 3.8.5

# install the compression libraries
sudo apt-get install libbz2-dev liblzma-dev

# download and compile the python interpreter
pyenv install 3.8.5

# re-create the virtual environment and activate it
pyenv virtualenv 3.8.5 dash_earthquakes
pyenv activate dash_earthquakes

# re-install all the dependencies
poetry install
```
