
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

TODO: Either include secrets file (see https://cloud.google.com/sdk/gcloud/reference/topic/gcloudignore) *OR* manage secrets with secret manager (https://cloud.google.com/run/docs/configuring/secrets).

### Notes:

Set project:

    gcloud config set project havistin

List properties:

    gcloud config list

Set default region:

    gcloud config set run/region europe-north1


# Todo

## Must

- Autoreload with gunicor, also templates
- Define static name for the container
- manage secrets with secret manager (https://cloud.google.com/run/docs/configuring/secrets).
- Set billing limit?

## Nice

- Refactor templating & separate html from code
- Lajit yleisyysjärjestyksessä, tai ainakin rarimmat myös

## Ideas

- One grid observation count or breeding index graph
- Better debug https://trstringer.com/python-flask-debug-docker-compose/

