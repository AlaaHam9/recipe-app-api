FROM python:3.9-alpine3.13
LABEL key="AlaaAlHameed"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
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
# jpeg-dev is not python package
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    # install dependencies for psycopg2 package (the adapter)
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install  -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then  /py/bin/pip install  -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    # create direcory to bu used to store media files  -p to create all of the subdirectories in the path that we specified
    mkdir -p /vol/web/media && \
    # static files
    # these are going to be the directories that are going to map to volumes that are going to be used to store our static and media files
    mkdir -p /vol/web/static && \
    # change the owner and the group recursivuly
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts


# this will updates the env variable inside the image , PATH is the env variable that automatically created on linux os
# so when we run any command in he project m we dont want to have to spesify the full path of out virtual envireoment
# ENV PATH="/py/bin:$PATH"
ENV PATH="/scripts:/py/bin:$PATH"

# must be the last line, any thinng will run from the image done by this user, we dont need the root privillage
USER django-user

# The name of the script that we are going to create that runs the application
# it is the default command that's run for dark containers that are spawned from the image that's build from this docker file
# When a container is started from the image, the specified script (run.sh in this case) will be executed by default
CMD [ "run.sh" ]