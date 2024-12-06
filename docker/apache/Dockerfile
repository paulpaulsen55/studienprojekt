FROM httpd:2.4.52-alpine

COPY composer.json composer.lock* ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install
RUN composer require guzzlehttp/guzzle


