FROM php:8.3.9-zts-alpine

RUN docker-php-ext-install pdo_mysql

WORKDIR /app

# install the parallel extension
RUN apt-get update; \
    apt-get install -y php-pear; \
    pecl install parallel; \
    echo "extension=parallel" > /usr/local/lib/php.ini
    
EXPOSE 8080

# Start the PHP server
CMD ["php", "-S", "0.0.0.0:8080", "-t", "/app/src/public"]
