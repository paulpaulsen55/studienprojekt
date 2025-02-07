# Concurrency Modelle für PHP
Dieses Repository enthält den Quellcode für das Studienprojekt 2.

## Voraussetzungen
nginx, Apache und Entwicklungsserver:
- [Docker](https://docs.docker.com/get-docker/)
IIS unter Windows:
- [Composer](https://getcomposer.org/Composer-Setup.exe) für Windows

## IIS
Für den IIS-Server muss noch eine manuelle installation auf dem Host-Betriebssystem durchgeführt werden (getestet auf Windows 11 Pro 24H2 Betriebssystembuild 26100.3037).
Schritte:

1. PHP installieren: 
    - [PHP 8.3.16 ZTS 64-Bit](https://downloads.php.net/~windows/pecl/releases/parallel/1.2.6/php_parallel-1.2.6-8.3-ts-vs16-x64.zip) herunterladen und entpacken nach `C:\php`
    - `C:\php` zum PATH hinzufügen
    - `php.ini` anpassen (; vor Zeile entfernen):
        ```ini
        extension=pdo_mysql
        ```
    - ggfs. [MariaDB connector installieren](https://mariadb.com/downloads/connectors/connectors-data-access/odbc-connector/)
    - Falls bei Testfall 2 curl error 60 auftritt, [cacert.pem](https://curl.se/ca/cacert.pem) herunterladen und in `C:\php\extras\ssl\cacert.pem` speichern. In `php.ini` folgendes Parameter ändern:
        ```ini
        curl.cainfo="C:\php\extras\ssl\cacert.pem"
        openssl.cafile="C:\php\extras\ssl\cacert.pem"
        ```
2. Repository klonen und Abhänigkeiten installieren: 
    ```shell
    git clone https://github.com/paulpaulsen55/studienprojekt.git
    cd studienprojekt
    composer install
    ```
3. parallel extension installieren:
    - [parallel 1.2.5 für PHP 8.3.x 64-Bit](https://downloads.php.net/~windows/pecl/releases/parallel/1.2.5/php_parallel-1.2.5-8.3-ts-vs16-x64.zip) herunterladen und die `php_parallel.dll` in `C:\php\ext` speichern und `pthreadsVC3.dll` in `C:\php` legen
    - `php.ini` anpassen (hinzufügen):
        ```ini
        extension=parallel
        ```
4. IIS-Server & Module installieren:
    - Server und CGI-Modul installieren: 
    ```shell 
    dism /online /enable-feature /featurename:IIS-WebServerRole /all
    dism /online /enable-feature /featurename:IIS-CGI /all
    ```
    - [URL Rewrite Modul 64-Bit](https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_de-DE.msi) installieren
    - IIS starten (WIN+R inetmgr oder IIS suchen) 
    - FastCGI in IIS konfigurieren (siehe [Anleitung ab Kapitel 8](https://hostadvice.com/how-to/web-hosting/how-to-install-php-with-fastcgi-extension-on-iis-7-iis-8-server/#paragraph8))
    - Webseite in IIS hinzufügen (R-Klick Websites > Website hinzufügen...):
      - Sitename: `studienprojekt`
      - Pfad: `C:\Users\%USERNAME%\studienprojekt\src\public` (wo das repository geklont wurde)
      - Port: 8030
5. Datenbank starten (Docker):
    ```shell
    docker-compose up -d db
    ```
Die Webseite ist nun unter [http://localhost:8030](http://localhost:8030) erreichbar.

## Apache, nginx, Entwicklungsserver
Starte das docker-compose file
```shell
docker-compose build
docker-compose up -d
```
Die verschiedenen Webserver sind unter folgenden Adressen zu erreichen:
- nginx: [http://localhost:8080](http://localhost:8080)
- apache: [http://localhost:8000](http://localhost:8000)
- dev: [http://localhost:8010](http://localhost:8010)

### Stoppen
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
Auch die Zeilenumbrüche können Probleme verursachen falls auf Windows entwickelt wird. Es wird empfohlen, die Dateien im Unix-Format zu speichern (LF).

## Weiteres zu Webservern
Die Anwendung, welche das SlimPHP Framework benutzt, kann mit verschiedensten Webservern betrieben werden ([siehe guide](https://www.slimframework.com/docs/v4/start/web-servers.html)).
