#FROM tiangolo/uwsgi-nginx-flask:python3.8
FROM python:3-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y gcc libgl1-mesa-glx libglib2.0-0
RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./app /havistin2/app

ENTRYPOINT gunicorn --chdir /havistin2/app main:app -w 2 --threads 2 -b 0.0.0.0:80

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

