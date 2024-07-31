# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 1.


## Prequisites
- [Docker](https://docs.docker.com/get-docker/)


## Ausführen
Starte das docker-compose file
```shell
docker-compose build # rebuilds the images
docker-compose up -d # starts the containers in the background
```
Die Anwendung ist nun unter [http://localhost:8080](http://localhost:8080) erreichbar.


## Stoppen
```shell
docker-compose down
```


## Entwicklung
Das `src` Verzeichnis enthält den Quellcode der Anwendung. Der Ordner wird in den Container gemountet, sodass Änderungen direkt in der Anwendung sichtbar sind.


## Weiteres
Die Anwendung kann mit verschiedenen Webservern wie Apache oder nginx betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)).
