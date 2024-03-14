# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 1.

## Prerequisite
| Name | Link |
| ---- | ---- |
| Composer | [Download Composer](https://getcomposer.org/download/) |
| Docker | [Download Docker](https://www.docker.com/products/docker-desktop/) |


## Install

```shell
composer install
```

## Run the application
Die Anwendung kann mit verschiedenen Webservern wie Apache oder nginx betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)). 
### PHP-Entwicklungsserver
Für eine schnelle Entwicklungsumgebung kann auch der interne PHP-Entwicklungsserver aus dem Ordner mit der index.php verwendet werden:
```shell
cd public
php -S localhost:8080
```

### nginx
nginx ist eine beliebte Webserver-Software, die für ihre hohe Leistung, Skalierbarkeit und Flexibilität bekannt ist.
```shell
docker-compose build
docker compose up -d
```