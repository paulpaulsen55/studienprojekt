FROM php:8.3.9-zts-alpine

# Install necessary dependencies and extensions
RUN apk update && apk add --no-cache \
    openrc \
    freetype-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    $PHPIZE_DEPS && \
    docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install gd && \
    docker-php-ext-install pdo_mysql && \
    pecl install parallel && \
    docker-php-ext-enable parallel

WORKDIR /app

# install composer and dependencies
COPY composer.json composer.lock* ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install