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
    ls /usr/local/lib/php/extensions/no-debug-zts-20230831/xdebug.so && \
    rm -rf /usr/src/xdebug && \
    apk del autoconf gcc make pkgconf git

# Verify Xdebug installation
RUN if [ ! -f /usr/local/lib/php/extensions/no-debug-zts-20230831/xdebug.so ]; then echo "Xdebug installation failed"; exit 1; fi

COPY /docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY /docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY /docker/nginx/xdebug.ini /usr/local/etc/php/conf.d/xdebug.ini

WORKDIR /app

COPY /docker/nginx/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]

EXPOSE 80

CMD ["sh", "-c", "php-fpm & nginx -g 'daemon off;'"]