FROM php:8.3.9-zts-alpine

RUN apk update && \
    apk add --no-cache apache2 apache2-utils && \
    sed -i '/LoadModule mpm_event_module/s/^/#/' /etc/apache2/httpd.conf && \
    sed -i '/LoadModule mpm_prefork_module/s/^#//g' /etc/apache2/httpd.conf

# Install necessary extensions
RUN apk update && apk add --no-cache \
    apache2 \
    freetype-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    $PHPIZE_DEPS && \
    docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install gd && \
    pecl install parallel && \
    docker-php-ext-enable parallel && \
    rm -rf /var/cache/apk/*

# Set the working directory
WORKDIR /var/www/localhost/htdocs

# install composer and dependencies
COPY composer.json composer.lock ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install

RUN sed -i 's/AllowOverride none/AllowOverride all/g' /etc/apache2/httpd.conf
RUN sed -i 's/DirectoryIndex index.html/DirectoryIndex index.php/' /etc/apache2/httpd.conf \
    && sed -i '/LoadModule rewrite_module/s/^#//g' /etc/apache2/httpd.conf
    # && sed -ri -e 's!/var/www!/app!g' /etc/apache2/httpd.conf

ENV PATH="/usr/local/bin:$PATH"

CMD ["httpd", "-D", "FOREGROUND"]