#!/bin/sh

php-fpm83 &
httpd -D FOREGROUND

exec "$@"