# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 2.

## Prequisites
nginx, Apache und Entwicklungsserver:
- [Docker](https://docs.docker.com/get-docker/)
IIS unter Windows:
- [Visual Studio 2019](https://www.computerbase.de/downloads/systemtools/entwicklung/visual-studio-2019/) mit MSVC (für IIS mit PHP 8.3.x)
- [Composer](https://getcomposer.org/Composer-Setup.exe) für Windows

## IIS/Windows
Für den IIS-Server muss noch eine manuelle installation auf dem Host-Betriebssystem durchgeführt werden. 
PHP muss hierzu kompiliert werden nach der [offiziellen Anleitung](https://wiki.php.net/internals/windows/stepbystepbuild_sdk_2). 
Nach der Installation von Visual Studio 2019 muss `namke` zum PATH hinzugefügt werden 
(C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64). 
Überprüfe die installtion indem der Befehl `nmake /?` die Hilfe zurückgibt. 
Folge der Anleitung weiter und kompiliere PHP mit folgenden Optionen:
```shell
dism /online /enable-feature /featurename:IIS-WebServerRole /all
dism /online /enable-feature /featurename:IIS-CGI /all
https://hostadvice.com/how-to/web-hosting/how-to-install-php-with-fastcgi-extension-on-iis-7-iis-8-server/
composer install
https://iis-umbraco.azurewebsites.net/downloads/microsoft/url-rewrite
https://downloads.php.net/~windows/pecl/releases/parallel/1.2.6/php_parallel-1.2.6-8.3-ts-vs16-x64.zip
```

## Ausführen
Starte das docker-compose file
```shell
docker-compose build # rebuilds the images
docker-compose up -d # starts the containers in the background
```
Die verschiedenen Webserver sind unter folgenden Adressen zu erreichen:
- nginx: [http://localhost:8080](http://localhost:8080)
- apache: [http://localhost:8000](http://localhost:8000)
- dev: [http://localhost:8010](http://localhost:8010)

## Stoppen
```shell
docker-compose down
```



## Entwicklung
Das `src` Verzeichnis enthält den Quellcode der Anwendung. Der Ordner wird in den Container gemountet, sodass Änderungen direkt in der Anwendung sichtbar sind.

## Fehlerbehebung
Fehler beim Starten der Docker-Container können durch bereits laufende Prozesse auf den Ports 8080, 8090 und 3306 verursacht werden. Diese müssen beendet werden, bevor die Container gestartet werden können. Bei anderen Problemen kann als letzte Lösung ein harter Reset durchgeführt werden (alternativ die betroffenen Container stoppen und entfernen):
```shell
docker system prune -a --volumes
```

## Weiteres zu Webservern
Die Anwendung, welche das SlimPHP Framework benutzt, kann mit verschiedensten Webservern betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)).
