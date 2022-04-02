#FROM tiangolo/uwsgi-nginx-flask:python3.8
FROM python:3-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Note that this copies app to /app/app/app.py
COPY . /app
WORKDIR /app
RUN chmod a+x ./gunicorn.sh

WORKDIR /app/app

ENTRYPOINT gunicorn main:app -w 2 --threads 2 -b 0.0.0.0:80



