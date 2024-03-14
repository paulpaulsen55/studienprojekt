FROM php:8.2-fpm-alpine

COPY . /var/www/html

RUN rm -rf /var/www/html/logs/* \
    && chown -R www-data:www-data /var/www/html