# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 1.

## Docker
Starte das docker-compose file
```shell
docker-compose build
docker-compose up -d
```

## Prequisites
- PHP 8.2.x ZTS
- parallel extension
- [Composer](https://getcomposer.org/)
- [XAMPP](https://www.apachefriends.org/de/faq_linux.html)


## Install

### PHP 8.2.x ZTS
```shell
sudo apt update
sudo apt install -y pkg-config build-essential autoconf bison re2c libxml2-dev libsqlite3-dev zlib1g-dev make # if not already installed
git clone https://github.com/php/php-src.git
cd php-src
git checkout php-8.2.11
./buildconf --force
./configure --enable-zts --with-mysql=mysqlnd --with-mysqli=mysqlnd --with-pdo-mysql=mysqlnd
make -j4
sudo make install
```

### parallel extension
```shell
sudo apt-get install php-pear # if not already installed
sudo pecl install parallel
cd /usr/local/lib
sudo nano php.ini
extension=parallel
```

### Composer dependencies
```shell
sudo apt install composer # if not already installed
composer install
```

## Run the application
Die Anwendung kann mit verschiedenen Webservern wie Apache oder nginx betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)). Für eine schnelle Entwicklungsumgebung kann auch der interne PHP-Entwicklungsserver aus dem Ordner mit der index.php verwendet werden:
```shell
cd src/public
php -S localhost:8080
```
