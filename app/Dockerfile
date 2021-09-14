# pull base image
FROM python:3.6.13-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 
ENV DJANGO_SUPERUSER_USERNAME="superuser" 
ENV DJANGO_SUPERUSER_PASSWORD="Password!" 
ENV DJANGO_SUPERUSER_EMAIL="mail@admin.com"
 
# copy requirements
COPY ./requirements.txt .

# install dependencies
RUN apt-get update \
    && apt-get -y install postgresql gcc python3 musl libcurl4-gnutls-dev librtmp-dev netcat  \
    && pip install --upgrade pip \
    && pip install -r requirements.txt 

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]