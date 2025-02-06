FROM alpine:latest

# Install necessary packages
RUN apk update && apk add --no-cache graphviz python3 py3-pip

# Install Python packages
RUN pip3 install graphviz

# Ensure executables have the correct permissions
RUN chmod +x /usr/bin/python3 /usr/bin/dot

# Copy webgrind files
COPY . /var/www/html

# Set the working directory
WORKDIR /var/www/html

# Expose the port
EXPOSE 80

# Start the web server
CMD ["php", "-S", "0.0.0.0:80", "-t", "/var/www/html"]