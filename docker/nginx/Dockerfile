FROM php-base:latest

# install nginx and dependencies
RUN apk update && apk add --no-cache \
    nginx \
    linux-headers \
    autoconf \
    gcc \
    make \
    pkgconf \
    git

# Compile and install Xdebug
RUN git clone https://github.com/xdebug/xdebug.git /usr/src/xdebug && \
    cd /usr/src/xdebug && \
    phpize && \
    ./configure && \
    make && make install && \
    rm -rf /usr/src/xdebug && \
    apk del autoconf gcc make pkgconf git

# After installing Xdebug, add:
RUN mkdir -p /usr/local/etc/php/conf.d && \
echo "zend_extension=xdebug.so" > /usr/local/etc/php/conf.d/xdebug.ini && \
echo "xdebug.mode=develop,profile" >> /usr/local/etc/php/conf.d/xdebug.ini && \
echo "xdebug.output_dir=/tmp" >> /usr/local/etc/php/conf.d/xdebug.ini && \
echo "xdebug.start_with_request=trigger" >> /usr/local/etc/php/conf.d/xdebug.ini

COPY /docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY /docker/nginx/default.conf /etc/nginx/conf.d/default.conf

WORKDIR /app

COPY /docker/nginx/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]

EXPOSE 80

CMD ["sh", "-c", "php-fpm & nginx -g 'daemon off;'"]