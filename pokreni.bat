@echo off
cd venv\Scripts & activate & cd ..\.. & py manage.py flush & py manage.py makemigrations & py manage.py migrate & py manage.py loaddata initial_MK2ZK_data.json & py manage.py runserver