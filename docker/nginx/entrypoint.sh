#!/bin/sh
chown -R www:www /app/src
exec "$@"