FROM php:8.1.28-zts

RUN docker-php-ext-install pdo_mysql

WORKDIR /app

# install the parallel extension
RUN apt-get update; \
    apt-get install -y php-pear; \
    pecl install parallel; \
    cd /usr/local/lib; \
    echo "extension=parallel" > php.ini
    
EXPOSE 8080

# Start the PHP server
CMD ["php", "-S", "0.0.0.0:8080", "-t", "/app/src/public"]
