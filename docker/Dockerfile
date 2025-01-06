FROM alpine:3.21

RUN apk update && apk add --no-cache \
    build-base \
    libxml2-dev \
    sqlite-dev \
    openssl-dev \
    freetype-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    git

# Download and configure PHP
RUN cd /tmp && \
    wget https://www.php.net/distributions/php-8.3.9.tar.gz && \
    tar -xvf php-8.3.9.tar.gz && \
    cd php-8.3.9 && \
    ./configure \
        --with-pdo-mysql \
        --enable-zts \
        --with-fpm \
        --with-fpm-user=www-data \
        --with-fpm-group=www-data \
        --with-openssl \
        --with-gd \
        --with-jpeg \
        --with-freetype && \
    make -j$(nproc) && make install

COPY php.ini /usr/local/lib/php.ini

RUN apk add autoconf
RUN git clone --branch=v1.2.5 --depth=1 https://github.com/krakjoe/parallel.git /usr/src/ext-parallel && \
    cd /usr/src/ext-parallel && \
    phpize && ./configure --enable-parallel && make && make test && make install

WORKDIR /app

# install composer and dependencies
COPY composer.json composer.lock* ./
RUN wget -q -O - https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install --optimize-autoloader