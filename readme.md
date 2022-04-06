
# Havistin 2

Tools to view and manage biodiversity data (with Python)

# Setup

Based on https://medium.com/thedevproject/setup-flask-project-using-docker-and-gunicorn-4dcaaa829620

## Running in development

First build the image:

    docker build -t havistin2-gunicorn:0.1 -t havistin2-gunicorn:latest .

Run with docker-compose

    docker-compose up; docker-compose down;

## Running in production

First build the image, see above. 

Test running with docker run:

    docker run -ti -p 80:80 havistin2-gunicorn:latest

Deploy:

     gcloud run deploy --port=80
     OR
     gcloud run deploy --port=80 --source .

https://havistin2-k4otrvyhmq-lz.a.run.app

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

- Custom domain

## Should

- Define static name for the container
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
- Chart with record per day (B, C, D) from each obs system & total.
- Geographic center of observations, day by day, on a xy-chart with Finnish border 

- One grid observation count or breeding index graph
- Better debug https://trstringer.com/python-flask-debug-docker-compose/

