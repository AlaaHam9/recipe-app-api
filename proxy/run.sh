#!/bin/bash

set -e

# copy default conf to  /etc/nginx/conf.d/default.conf on docker image, envsubst replace the env variable by the values
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
#  Start nginx in foreground

nginx -g 'daemon off;'