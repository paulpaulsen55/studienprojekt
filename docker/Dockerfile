FROM php:8.3.9-zts-alpine

RUN docker-php-ext-install pdo_mysql

WORKDIR /app

# install composer and dependencies
COPY composer.json composer.lock* ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install

# install parallel extension
RUN apk add --no-cache $PHPIZE_DEPS \
    && pecl install parallel \
    && docker-php-ext-enable parallel

EXPOSE 8080

# Start the PHP server
CMD ["php", "-S", "0.0.0.0:8080", "-t", "/app/src/public"]
