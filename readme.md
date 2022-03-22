

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

## Misc


docker-compose run web python3 -m pdb main.py

Build:

docker build -t myflask ./

docker-compose up --build -d


https://trstringer.com/python-flask-debug-docker-compose/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

