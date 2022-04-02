
# Havistin 2
Tools to view and manage biodiversity data (with Python)

# Notes

## Running in production

Build:

docker build -t havistin2-gunicorn:0.1 -t havistin2-gunicorn:latest .

Run with docker run

docker run -ti -p 80:80 havistin2-gunicorn:latest

Or run with docker-compose

## Todo:

Define static name for the container

# Ideas

One grid observation count or breeding index graph

Try Gunicorn instead?


## Misc

Build:

docker build -t havistin2 .



docker-compose run web python3 -m pdb main.py


docker-compose up --build -d


https://trstringer.com/python-flask-debug-docker-compose/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt



DAMN ! worker 1 (pid: 89) died :( trying respawn ..
https://github.com/unbit/uwsgi/issues/1779

# Todo

## Must

- Deployment:`
- Test without docker-compose
    - Secrets as env variable?
    - Settings as en variable?
- Gunicorn?


## Nice

- Refactor templating & separate html from code
- Lajit yleisyysjärjestyksessä, tai ainakin rarimmat myös
