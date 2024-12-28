
# Havistin 2

Tools to view biodiversity data and Finnish bird atlas.

Uses Python, Flask, Redis (for caching), MongoDB (for weather data), Chart.js, Docker & Docker-Compose, and is deployed with Google Cloud Run.

# Setup

* Clone this repo
* Set secrets to `app/app_secrets.py` (see example file in the directory)
* Set up your OpenAI API key as `OPENAI_API_KEY` in `example.env`, and rename it to `.env`. (This affects the news page on localhost development environment.)
* `docker compose up; docker compose down;`

Based on https://medium.com/thedevproject/setup-flask-project-using-docker-and-gunicorn-4dcaaa829620

Flush cache: localhost/flush

## Setting weather messaging

With crontab, call http://localhost/weather/change/1 every 10 minutes. The parameter "1" sets messaging on.

It's better to call this at 5, 15, 25, 35 45 and 55 past, so that data has been updated from weather stations to the API.

## Running in development

First build the image, and tag it as latest:

    docker build -t havistin2-gunicorn:latest .

Or, build with Docker Compose:

    docker compose up --build; docker compose down;

Run in development mode with Docker Compose. This serves the app on localhost and auto-reloads changes to script files, and to other files (like templates) defined on docker-compose.yml.

    docker compose up; docker compose down;

To run without Docker-compose:

    docker run -ti -p 80:80 havistin2-gunicorn:latest

### Login to localhost

Login normally. When redirected to production app, change havistin.biomi.org to localhost.

## Running in production with Google Cloud Run & Redis

Set up Redis to be used for caching. Store Redis server name & credentials to `app_secrets.py`. The app can be run also without Redis cache; just comment out Redis cache on `main.py` and use Filesystem cache instead.

Set up your OpenAI API key to Google Cloud Run environment variables (Project > Edit & Deploy New Revision > Variables & Secrets > Add Variable).

Deploy to Google Cloud Run:

    gcloud run deploy havistin2 --port=80 --max-instances=4 --concurrency=10 --memory=1024Mi --timeout=40 --source .

Redeploy from Google Console (https://console.cloud.google.com/run) if you want to set more options there.

Some pages under havistin.biomi.org are fetched regularly using Google Cloud Scheduler, to update caches.

### Issues

If build fails due to "Could not build wheels for pandas...", try updating pandas version on requirements.txt.  

If site fails with message "Service Unavailable", check logs and try assigning more memory. Also check that .gcloudignore doesn't exclude necessary files.

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

- User accessing my page without logging in -> login page
- Why this doesn't work: http://localhost/taxa/species/MX.205966
- Complete lists per square:
    - router, page and template
    - fetch data from api
    - add map functions into the common helper file
    - call common helpers/squares_with_data
    - define color function: grayscale capped 100

## My observations; ideas

- species per phylum
- observations total count & average per day

## Should / Might

- Add nonce to scripts
- robots.txt, forbid all but front page (now all forbidden)
- Paginate fetching mappable observations of a square. Or increase page size? Must do this before top square has less than 1000 mappable observations.
- Command to deploy version other than latest. First submit to Articat Registry, then deploy from there using --image option.
- Country filtering? (bots)
- Moving from existing to nonexisting grid should show message, not error

## Nice / Ideas

- Last week bird abundance vs. week before
- Animated species distribution over time
- Refactor templating & separate html from code
- Lajit yleisyysjärjestyksessä, tai ainakin rarimmat myös
- Reloading with inotify, see https://docs.gunicorn.org/en/stable/settings.html
- Gamification: show how much my today's observations increased pv-summa
    - User logs in
    - User gives square and date
    - Get aggregate of observations by species, atlasClass, filter Aves, Finland, 2022-01-01 ... given date - 1, grid, quality, atlasClassB/C/D, rank=species
    - Calculate pv-sum by going through each species, and doing if/else checking if D, C, or B exist.
    - Get similar aggregate, but only my observations only today
    - Calculate how much pv-sum increases by going through my observations each species, and comparing to class of previous aggregate 
- People lists:
    - People with complete lists from most squares: https://ebird.org/atlasny/top100?region=New+York&locInfo.regionCode=US-NY&rankedBy=blocks_with_complete
        - needs complete checklist search
- Refactor? data generation into shared module
- manage secrets with secret manager (https://cloud.google.com/run/docs/configuring/secrets).
- Optimize gunicorn & dockerfile?
- Port as env var, instead of setting on deploy-time or using default (8080?)
- Geographic center of observations, day by day, on a xy-chart with Finnish border 
- One grid observation count or breeding index graph
- Better debug https://trstringer.com/python-flask-debug-docker-compose/

## GPS working logic

- As user, I might want to 
    - Have GPS define my location, and see square informatn with a map that confirms where I am
    - Select the square by myself
    - Redfine my location when I have moved
- GPS Page A, that gets location from GPS, and redirects to square page B
- Square page B, that shows square information. Has two features: a) link to page A ("Hae sijaintini uudelleen") and b) selection for square ("valitse ruutu")

## Notes

### Session data

´´main.py/@app.context_processor´´ decorator makes session data available on each template. However, if you want session data to be available on an external page function (e.g. ´´atlas.atlas.main()´´), you need to pass it to it manually.

Caching and session data can work together in few ways:

1) Don't use caching on pages that require user information
2) Cache the base page (SSR), then update user information with Javascript
3) Cache functions instead of routes

