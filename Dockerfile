FROM tiangolo/uwsgi-nginx-flask:python3.8
#FROM tiangolo/meinheld-gunicorn-flask:python3.8

#WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./app /app

# Test if image built with this can be deployed to Google Cloud
# CMD uwsgi --http :80

#CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:80", "app:main"]
