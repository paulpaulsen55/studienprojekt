FROM php-base:latest

# install apache and dependencies
RUN apk update && apk add --no-cache \
    apache2 \
    apache2-ssl \
    php83-apache2 

# copy apache configuration
# COPY docker/apache/httpd.conf /etc/apache2/httpd.conf


# Apache settings
RUN sed -i 's/^#ServerName .*/ServerName localhost:80/g' /etc/apache2/httpd.conf && \
    sed -i 's/^LoadModule php7_module.*/LoadModule php7_module modules\/libphp7\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/^#LoadModule rewrite_module.*/LoadModule rewrite_module modules\/mod_rewrite\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/^#LoadModule deflate_module.*/LoadModule deflate_module modules\/mod_deflate\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/DirectoryIndex index\.html/DirectoryIndex index\.php/g' /etc/apache2/httpd.conf && \
    sed -i 's/\/var\/www\/localhost\/htdocs/\/app\/src/g' /etc/apache2/httpd.conf && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/httpd.conf
RUN echo "AddType application/x-httpd-php .php" >> /etc/apache2/httpd.conf
RUN sed -i 's|/app/src|/app/src/public|g' /etc/apache2/httpd.conf


# && \
#     mkdir -p /var/www/localhost/htdocs && \
#     chown apache:apache /var/log/apache2 && \
#     chown apache:apache /var/www/localhost/htdocs && \
#     mkdir /run/apache2 && \
    # chown apache:apache /run/apache2

RUN apk add procps

CMD ["httpd", "-D", "FOREGROUND"]