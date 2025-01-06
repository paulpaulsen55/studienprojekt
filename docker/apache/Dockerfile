FROM php-base:latest

# install apache and dependencies
RUN apk update && apk add --no-cache \
    apache2 \
    apache2-proxy \
    php83-fpm \
    php83-pdo php83-pdo_mysql
    # php-apache2
    # php82-apache2
    # php83-pdo \
    # php83-pdo_mysql

# Apache settings
RUN sed -i 's/^#ServerName .*/ServerName localhost:80/g' /etc/apache2/httpd.conf && \
    sed -i 's/^LoadModule php7_module.*/LoadModule php7_module modules\/libphp7\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/^#LoadModule rewrite_module.*/LoadModule rewrite_module modules\/mod_rewrite\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/^#LoadModule deflate_module.*/LoadModule deflate_module modules\/mod_deflate\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/DirectoryIndex index\.html/DirectoryIndex index\.php/g' /etc/apache2/httpd.conf && \
    sed -i 's/\/var\/www\/localhost\/htdocs/\/app\/src\/public/g' /etc/apache2/httpd.conf && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/httpd.conf
# RUN echo "AddType application/x-httpd-php .php" >> /etc/apache2/httpd.conf
# RUN sed -i 's/^LoadModule php7_module.*/LoadModule php_module modules\/libphp.so/g' /etc/apache2/httpd.conf


RUN sed -i 's/^#LoadModule mpm_event_module.*/LoadModule mpm_event_module modules\/mod_mpm_event\.so/g' /etc/apache2/httpd.conf && \
    sed -i 's/^LoadModule mpm_prefork_module.*/#LoadModule mpm_prefork_module modules\/mod_mpm_prefork\.so/g' /etc/apache2/httpd.conf

    RUN echo '<FilesMatch \.php$>' >> /etc/apache2/httpd.conf && \
        echo '    SetHandler "proxy:fcgi://127.0.0.1:9000"' >> /etc/apache2/httpd.conf && \
        echo '</FilesMatch>' >> /etc/apache2/httpd.conf
    
RUN echo '<IfModule mime_module>' >> /etc/apache2/httpd.conf && \
    echo 'AddType application/x-httpd-php .php' >> /etc/apache2/httpd.conf && \
    echo '</IfModule>' >> /etc/apache2/httpd.conf

    RUN echo 'user = apache' >> /etc/php83/php-fpm.conf && \
        echo 'group = apache' >> /etc/php83/php-fpm.conf && \
        echo 'listen = 127.0.0.1:9000' >> /etc/php83/php-fpm.conf

# COPY /docker/apache/php.conf /etc/apache2/conf.d/php.conf
COPY /docker/apache/a2manage.sh /app
# RUN ./a2manage.sh a2enmod php8.3

COPY /docker/apache/entrypoint.sh /app
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]

# CMD ["httpd", "-D", "FOREGROUND"]