FROM python:3.8-alpine

ARG build_version
ENV BUILD_VERSION=${build_version}

ARG develop
ENV DEVELOP=${develop}

ENV USER=app-user
ENV UID=900
ENV GID=901

RUN addgroup --gid "$GID" "$USER" && adduser -D -H -u "$UID" "$USER" -G "$USER"

# hadolint ignore=DL3013,DL3018
RUN apk update && \
	apk --no-cache add postgresql-dev gcc python3-dev musl-dev && \
	pip3 install --upgrade pip

WORKDIR /service
RUN chown -R "$USER":"$USER" /service

COPY ./requirements /service/requirements
COPY ./requirements.txt /service/requirements.txt

RUN pip3 install -r requirements.txt && \
    if [ $DEVELOP ]; then \
        pip3 install -r /service/requirements/development.txt; \
    fi

COPY . /service

USER "$USER"
ENTRYPOINT ["/service/entrypoint.sh"]
