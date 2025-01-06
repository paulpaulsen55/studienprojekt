FROM php-base:latest

# install apache and dependencies
RUN apk update && apk add --no-cache \
    apache2 \
    apache2-proxy

# Apache settings
RUN sed -i 's/^#ServerName .*/ServerName localhost:80/g' /etc/apache2/httpd.conf
RUN sed -i 's/DirectoryIndex index.html/DirectoryIndex index.php/g' /etc/apache2/httpd.conf
RUN sed -i 's/\/var\/www\/localhost\/htdocs/\/app\/src\/public/g' /etc/apache2/httpd.conf
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/httpd.conf
RUN sed -i 's/#LoadModule rewrite_module modules\/mod_rewrite.so/LoadModule rewrite_module modules\/mod_rewrite.so/g' /etc/apache2/httpd.conf
RUN echo "AddType application/x-httpd-php .php" >> /etc/apache2/httpd.conf
RUN sed -i '/<Directory \/>/,/<\/Directory>/d' /etc/apache2/httpd.conf

RUN echo '<FilesMatch .php$>' >> /etc/apache2/httpd.conf && \
    echo '    SetHandler "proxy:fcgi://127.0.0.1:9000"' >> /etc/apache2/httpd.conf && \
    echo '</FilesMatch>' >> /etc/apache2/httpd.conf

COPY /docker/apache/a2manage.sh /app
RUN ./a2manage.sh a2dismod mpm_prefork
RUN ./a2manage.sh a2enmod mpm_event
RUN ./a2manage.sh a2enmod proxy proxy_fcgi

CMD ["sh", "-c", "php-fpm & httpd -D FOREGROUND"]