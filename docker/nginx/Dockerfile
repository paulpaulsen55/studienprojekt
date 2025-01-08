FROM php-base:latest

# install nginx and dependencies
RUN apk update && apk add --no-cache \
    nginx

COPY /docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY /docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# Configure Nginx similar to Apache's configuration
# Add additional configuration as needed

WORKDIR /app

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]