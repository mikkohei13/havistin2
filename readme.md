
# Havistin 2
Tools to view and manage biodiversity data (with Python)

# Notes

## Running in production

Settings in docker-compose are for developing the app. When deploying, you should somehow set

- Production uWSGI server. This is included in the docker image
- FLASK_DEBUG=1 -> does not reload changes automatically
- IP address

Also:

- Remove autoloader from uwsgi.ini
- Remove debug=True on main.py


## Gunicorn

Try Gunicorn instead?

# Ideas

One grid observation count or breeding index graph


## Misc


docker-compose run web python3 -m pdb main.py

Build:

docker build -t havistin2 .


docker-compose up --build -d


https://trstringer.com/python-flask-debug-docker-compose/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt



DAMN ! worker 1 (pid: 89) died :( trying respawn ..
https://github.com/unbit/uwsgi/issues/1779
