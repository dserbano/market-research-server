## Local Development 

+ cd app
+ django-env\Scripts\activate.bat
+ python manage.py migrate
+ python manage.py runserver

## Local Docker 

+ docker-compose down -v
+ docker-compose build
+ docker-compose up -d

## Deploy on EC2

+ ssh -i "market-research-keys2.pem" ec2-user@ec2-18-195-56-138.eu-central-1.compute.amazonaws.com
+ cd market-research-server
+ sudo git pull
+ sudo docker-compose -f docker-compose.prod.yml down -v
+ sudo docker-compose -f docker-compose.prod.yml up -d --build
+ sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
+ sudo docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

## Create an App

python3 django-env\Scripts\django-admin.py startapp AppName

## Production Link

http://ec2-18-195-56-138.eu-central-1.compute.amazonaws.com/

