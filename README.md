# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 1.

## Prequisites
- PHP 8.2.x ZTS
- parallel extension
- Composer


## Install

### PHP 8.2.x ZTS
```shell
git clone https://github.com/php/php-src.git
cd php-src
git checkout php-8.2.11
./buildconf --force
./configure --enable-zts
make -j4
make install
```

### parallel extension
```shell
sudo apt-get install php-pear # if not already installed
sudo pecl install parallel
```

### Composer dependencies
```shell
sudo apt install composer # if not already installed
composer install
```

## Run the application
Die Anwendung kann mit verschiedenen Webservern wie Apache oder nginx betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)). Für eine schnelle Entwicklungsumgebung kann auch der interne PHP-Entwicklungsserver aus dem Ordner mit der index.php verwendet werden:
```shell
cd public
php -S localhost:8080
```
