FROM microsoft/windows-servercore-iis:windowsservercore-ltsc2025

RUN powershell -NoProfile -Command Remove-Item -Recurse C:\inetpub\wwwroot\*

WORKDIR /inetpub/wwwroot

COPY content/ .

