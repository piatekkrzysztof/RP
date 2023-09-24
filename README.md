# Recruitment Project
This project using Django and Django REST Framework. Application is containerized by docker

Requirements:
Docker
Docker-compose
Python 3.11

Setup and config
Django:
Update the settings in 'settings.py' according to your requirements, pay attention to 
DATABASE settings. Set your database name, password, host etc.Use same settings in 
docker-compose file in db settings.
Docker:
If you downloaded repository, just navigate to project folder:
cd <rp>
And build docker container:
docker-compose up --build

*All other dependencies from 'requirements.txt' will be installed by docker

After the containers are up, you can create superuser in terminal:

docker-compose exec web python manage.py createsuperuser

Access 

When the containers are up, you can access the django application by navigating
to: http://localhost:8000/

Visit http://localhost:8000/admin/ to create new users and tiers

