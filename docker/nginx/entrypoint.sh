#!/bin/sh
adduser www nginx 
chown -R www:www /app/src
chmod 0755 /var/lib/nginx/tmp
exec "$@"