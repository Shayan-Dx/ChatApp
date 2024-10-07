# ChatApp

A simple chatapp made mainly with django and rest framework

instruction to use the project :
1-clone the project using git clone
2-create an .env file and include the stuff that i noted in the pay attention to
3-run docker-compose up --build

things that you need to pay attention to :
1-make sure to create an .env file and include these variables in it:
SECRET_KEY (django secret key)
DATABASE VARIABLES (such as name - username - password - host - port)
2-make sure to use the command (docker-compose exec web python manage.py createsuperuser) to create an superuser to access the database
