FROM alpine:3.21

RUN apk update && apk add --no-cache \
    build-base \
    libxml2-dev \
    sqlite-dev \
    openssl-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    freetype-dev \
    autoconf \
    git

# download and configure PHP
RUN cd /tmp && \
    wget https://www.php.net/distributions/php-8.3.9.tar.gz && \
    tar -xvf php-8.3.9.tar.gz && \
    cd php-8.3.9 && \
    ./configure \
        --with-pdo-mysql \
        --enable-zts \
        --enable-fpm \
        --with-fpm-user=apache \
        --with-fpm-group=apache \
        --with-openssl \
        --enable-gd \
        --with-jpeg=/usr/include \
        --with-freetype=/usr/include && \
    make -j$(nproc) && make install

COPY /docker/php.ini /usr/local/lib/php.ini

# configure PHP-FPM
COPY /docker/php-fpm.conf /usr/local/etc/php-fpm.conf
RUN mkdir -p /var/log/php-fpm && \
    touch /var/log/php-fpm/error.log

# install parallel extension
RUN git clone --branch=v1.2.5 --depth=1 https://github.com/krakjoe/parallel.git /usr/src/ext-parallel && \
    cd /usr/src/ext-parallel && \
    phpize && ./configure --enable-parallel && make && make test && make install

WORKDIR /app

# install composer and dependencies
COPY composer.json composer.lock* ./
RUN wget -q -O - https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install --optimize-autoloader

RUN addgroup -S www && adduser -S -D -G www www