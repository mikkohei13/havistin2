
# Havistin 2

Tools to view and manage biodiversity data and Finnish bird atlas.

Uses Python, Flask, Docker & Docker-Compose and Chart.js, and is deployed with Google Cloud Run.

# Setup

* Clone this repo
* Set secrets to app/app_secrets.py (see example file in the directory)
* `docker-compose up; docker-compose down;`

Based on https://medium.com/thedevproject/setup-flask-project-using-docker-and-gunicorn-4dcaaa829620

Flush cache: root-URL/flush

## Setting weather messaging

With crontab, call http://localhost/weather/change every 10 minutes.

It's better to call this at 5, 15, 25, 35 45 and 55 past, so that data has been updated from weather stations to the API.

## Running in development

First build the image, and tag it with a version number and/or as latest:

    docker build -t havistin2-gunicorn:VERSIONNUMBER -t havistin2-gunicorn:latest .

Or set a version number:

    docker build -t havistin2-gunicorn:VERSIONNUMBER -t havistin2-gunicorn:latest .

Check which version numbers have been used:

    docker image ls

Run in development mode with Docker-compose. This serves the app on localhost and auto-reloads changes to script files, and to other files (like templates) defined on docker-compose.yml.

    docker-compose up; docker-compose down;

To run without Docker-compose:

    docker run -ti -p 80:80 havistin2-gunicorn:latest

## Running in production with Google Cloud Run & Redis

Set up Redis to be used for caching. Store Redis server name & credentials to app_secrets.py.

The app can be run also without Redis cache; just comment out Redis cache on main.py and use Filesystem cache instead.

Deploy to Google Cloud Run:

    gcloud run deploy havistin2 --port=80 --max-instances=4 --concurrency=10 --memory=512Mi --timeout=40 --source .

Redeploy from Google Console (https://console.cloud.google.com/run) if you want to set more options there.

If build fails due to "Could not build wheels for pandas...", try updating pandas version on requirements.txt.  

Some pages under havistin.biomi.org are fetched regularly using Google Cloud Scheduler, to update caches.

## Google Cloud Run notes:

Three ways to handle secrets:

- Recommended: using  secret manager (https://cloud.google.com/run/docs/configuring/secrets)
- Using environment variables, but they can be seen by all project users
- Using local secrets file, which is excluded from Git but included in the cloud. You can ot do continuous integration with this option.

Five ways (at least) to deploy:

- From source files (some langs)
- Fron source Dockerfile (any lang)
- From Docker Hub
- From Artifact Registry
- Continuous integration with Github

Cloud build page: https://console.cloud.google.com/cloud-build

Set project:

    gcloud config set project havistin

List properties:

    gcloud config list

Set default region:

    gcloud config set run/region europe-north1

List repositories:

    gcloud artifacts repositories list

Build image from Dockerfile:

    gcloud config get-value project
    gcloud builds submit --tag europe-north1-docker.pkg.dev/PROJECT-ID/havistin/havistin2:0.1example


# Todo

## Must

- Refactor common functions into common
- robots.txt, forbid all but front page (now all forbidden)
- Paginate fetching mappable observations of a square. Or increase page size? Must do this before top square has less than 1000 mappable observations.
- Birds of prey on adjusted form
- Command to deploy version other than latest. First submit to Articat Registry, then deploy from there using --image option.
- Country filtering? (bots)
- Moving from existing to nonexisting grid should show message, not error


## Should / Might

- Gamification: show how much my today's observations increased pv-summa
    - User logs in
    - User gives square and date
    - Get aggregate of observations by species, atlasClass, filter Aves, Finland, 2022-01-01 ... given date - 1, grid, quality, atlasClassB/C/D, rank=species
    - Calculate pv-sum by going through each species, and doing if/else checking if D, C, or B exist.
    - Get similar aggregate, but only my observations only today
    - Calculate how much pv-sum increases by going through my observations each species, and comparing to class of previous aggregate 
- Species page with time graph (x: time, y: atlascode) 
- People lists:
    - People with complete lists from most squares: https://ebird.org/atlasny/top100?region=New+York&locInfo.regionCode=US-NY&rankedBy=blocks_with_complete
        - needs complete checklist search
- Refactor? data generation into shared module
- manage secrets with secret manager (https://cloud.google.com/run/docs/configuring/secrets).
- Optimize gunicorn & dockerfile?
- Port as env var, instead of setting on deploy-time or using default (8080?)
- Secret management

## Nice

- Refactor templating & separate html from code
- Lajit yleisyysjärjestyksessä, tai ainakin rarimmat myös
- Reloading with inotify, see https://docs.gunicorn.org/en/stable/settings.html

## Ideas

- Ruutulomake
   - link to map
- Geographic center of observations, day by day, on a xy-chart with Finnish border 

- One grid observation count or breeding index graph
- Better debug https://trstringer.com/python-flask-debug-docker-compose/

