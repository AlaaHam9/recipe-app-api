FROM python:3.9-alpine3.13
LABEL key="AlaaAlHameed"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# this value will override in docker compose file
ARG DEV=false

# we will run below command on alpine image
# create vertual enviroment for dependecies
# upgrade pip for this virtual env that we created in previous step
# install the requirements
# remove the tmp directory
# add new user inside the image to dont use the root user
RUN python -m venv /py && \   
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    # install dependencies for psycopg2 package (the adapter)
        build-base postgresql-dev musl-dev && \   
    /py/bin/pip install  -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then  /py/bin/pip install  -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# this will updates the env variable inside the image , PATH is the env variable that automatically created on linux os
# so when we run any command in he project m we dont want to have to spesify the full path of out virtual envireoment
ENV PATH="/py/bin:$PATH"

# must be the last line, any thinng will run from the image done by this user, we dont need the root privillage
USER django-user
