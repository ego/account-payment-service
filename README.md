# Account payment service

## Service feature

* Send payment from one account to another
* Send payments only with same currency
* View all payments
* View all accounts


## System design

* [Python 3.8](https://www.python.org/ "Python 3.8")
* [Django 2.2.6](https://www.djangoproject.com "Django 2.2.6")
* [Django REST framework 3.10.3](https://www.django-rest-framework.org "Django REST framework 3.10.3")
* [PostgreSQL 12](https://www.postgresql.org/docs/12/index.html "PostgreSQL 12")
* [Nginx 1.17.6](https://nginx.org "Nginx 1.17.6")


## System requirements


``` bash
make --version
>= GNU Make 3.81
```

```bash
docker --version
>= Docker version 19.03.5, build 633a0ea
```

```
docker-compose --version
>= docker-compose version 1.24.1, build 4667896b
```


## REST API

Nginx reverse proxy on `80`
http://localhost/api/v1/

Dev app runs on `8888`
http://localhost:8888/api/v1/


## Development

Make and Makefile for commands
```bash
make help
```

Docker compose files:

* `docker-compose.yml` **production** build
* `docker-compose.dev.yml` **development** build
  Override `ENV` vars and allow databases log queries


`ENV` vars:

* `app.env`
* `postgres.env`


**Run dev application**

```bash
make
```

**Run prod application**

```bash
make up-prod
make ps-prod
make down-prod
```

`make up-prod` run's reverse proxy so you can scale your application.
Variable `SCALE` in `Makefile`.


Coding

```bash
make test
make check
make refactor
```
