# Project vars
PROJECT = accounts
SERVICE = web
DB = pg
NG = nginx
DC_PROD = docker-compose -p $(PROJECT) -f docker-compose.yml
DC = $(DC_PROD) -f docker-compose.dev.yml
SRC = .
UP = ..
SCALE = web=3
APPS = accounts payments

# Main targets
up:
	$(DC) up -d --build

help:
	@echo "  up-prod    docker-compose up project $(PROJECT) with production build"
	@echo "  down-prod  docker-compose down production build"
	@echo "  up         docker-compose build and up project $(PROJECT) with dev build"
	@echo "  restart    docker-compose restart"
	@echo "  ps         docker-compose ps"
	@echo "  bash       app $(SERVICE) bash"
	@echo "  log        app $(SERVICE) log"
	@echo "  attach     app $(SERVICE) attach (for python breakpoint())"
	@echo "  bash-pg    DB $(DB) bash"
	@echo "  psql       DB $(DB) psql"
	@echo "  test       run project tests"
	@echo "  check      check code"
	@echo "  refactor   format code"
	@echo "  clean      clean dev staff"
	@echo "  ...        all commands in Makefile"

# Prod
up-prod:
	$(DC_PROD) up -d --build --scale $(SCALE)
down-prod:
	$(DC_PROD) down --rmi local --remove-orphans
ps-prod:
	$(DC_PROD) ps

# Dev docker targets
build:
	$(DC) build
stop:
	$(DC) stop
down:
	$(DC) down --rmi local --remove-orphans
build-no-cache:
	$(DC) build --no-cache
restart: stop down build up
	@echo "docker-compose has ben restarted!"
ps:
	$(DC) ps

# Test and code
test cov cover coverage: check
	$(DC) exec $(SERVICE) /bin/sh -c 'coverage erase && coverage run --rcfil $(UP)/setup.cfg manage.py test && coverage report'
	@echo "Tests done!"
check: safety flake8 black pylint
	@echo "Check done!"
refactor: isort autopep8-refactor autoflake-refactor black-refactor
	@echo "Refactor done!"

# $(SERVICE) targets
bash:
	$(DC) exec -e COLUMNS="`tput cols`" -e LINES="`tput lines`" $(SERVICE) /bin/sh
log:
	$(DC) logs -f $(SERVICE)
attach:
	docker attach $(PROJECT)_$(SERVICE)_1

# $(DB) targets
bash-pg:
	$(DC) exec -e COLUMNS="`tput cols`" -e LINES="`tput lines`" $(DB) /bin/sh
psql:
	$(DC) exec $(DB) psql accounts_db -h localhost -U accounts_user
log-pg:
	$(DC) logs -f $(DB)
# Dev mode, log all DB queries
psql-log:
	$(DC) exec $(DB) /bin/sh -c 'tail -f /var/lib/postgresql/data/log/postgresql*.log'
bash-nginx:
	$(DC) exec -e COLUMNS="`tput cols`" -e LINES="`tput lines`" $(NG) /bin/sh

# Tools
isort:
	$(DC) exec $(SERVICE) isort --recursive $(SRC)
safety:
	$(DC) exec $(SERVICE) /bin/sh -c 'safety check && safety check -r $(UP)/requirements.txt && bandit -r .'
radon:
	$(DC) exec $(SERVICE) radon cc .
	@echo "https://radon.readthedocs.io/en/latest/commandline.html"
flake8:
	$(DC) exec $(SERVICE) flake8 --config $(UP)/setup.cfg $(SRC)
black:
	$(DC) exec $(SERVICE) black --check --diff --config $(UP)/black.toml $(SRC)
pylint:
	$(DC) exec $(SERVICE) pylint --rcfile $(UP)/setup.cfg $(APPS)

# Autoformat and refactor
autopep8-refactor:
	$(DC) exec $(SERVICE) autopep8 --verbose --recursive --in-place -a -a $(SRC)
autoflake-refactor:
	$(DC) exec $(SERVICE) autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports $(SRC)
black-refactor:
	$(DC) exec $(SERVICE) black --config $(UP)/black.toml $(SRC)

# Dockerfile validations
hadolint:
	docker run --rm -i hadolint/hadolint < Dockerfile

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf htmlcov
	rm -rf dist

.PHONY: all up build stop down build-no-cache restart ps bash log attach bash black flake8 pylint cov cover coverage check format hadolint clean
