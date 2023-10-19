# praktikum_new_diplom

# Demo
```
http://84.252.136.204
log: admin@mail.ru
pass: admin
```

- Create env-file:
```
touch .env
```
- Fill in the env-file like it:
```
DEBUG=False
SECRET_KEY=<Your_some_long_string>
ALLOWED_HOSTS='localhost, 127.0.0.1, <Your_host>'
CSRF_TRUSTED_ORIGINS='http://localhost, http://127.0.0.1, http://<Your_host>'
DB_ENGINE='django.db.backends.postgresql'
DB_NAME='postgres'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD=<Your_password>
DB_HOST='db'
DB_PORT=5432
```
- Copy files from 'infra/' (on your local machine) to your server:
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```
- Run docker-compose
```
sudo docker-compose up -d
```

# Команды Docker

Для первого деплоя создайте статику на сервере:
```bash
sudo docker exec -it foodgram-backend-1 python manage.py collectstatic --noinput
```

Makemigrations:
```bash
sudo docker exec -it foodgram-backend-1 python manage.py makemigrations --noinput
```

Migrations:
```bash
sudo docker exec -it foodgram-backend-1 python manage.py migrate --noinput
```

Загрузить ингридиенты ( data/ingredients.csv ):
```bash
sudo docker exec -it foodgram-backend-1 python manage.py load_ingrs
```

Загружить теги ( data/tags.csv | data/tags.json):
```bash
sudo docker exec -it foodgram-backend-1 python manage.py load_tags
```

Создать суперюзера Django - 
```bash
sudo docker exec -it foodgram-backend-1 python manage.py createsuperuser
```

# Команды:

Makemigrations:
```bash
python backend/manage.py makemigrations --noinput
```

Migrate:
```bash
python backend/manage.py migrate --noinput
```

Collectstatic:
```bash
python backend/manage.py collectstatic --noinput
```

Create Superuser:
```bash
python backend/manage.py createsuperuser
```

Run server:
```bash
python backend/manage.py runserver 0.0.0.0:8000
```

Make dump:
```bash
python -Xutf8 backend/manage.py dumpdata -o dump.json
```

Restore dump:
```bash
python backend/manage.py loaddata dump.json
```

