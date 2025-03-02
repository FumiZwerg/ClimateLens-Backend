# ClimateLens-Backend

Dieses Backend ist Teil eines Universitätsprojekts, im Rahmen des Kurses WWI22ABC-5 Projekt / Anwendungsentwicklung, an der DHBW VS.

Die Anwendung ermöglicht die Suche und Identifikation von Wetterstationen anhand spezifischer Koordinaten und Zeiträume. Für die ausgewählten Stationen werden sowohl die jährlichen Durchschnittswerte der minimalen und maximalen Temperaturen als auch der meteorologischen Jahreszeiten grafisch sowie textuell dargestellt.

Das Frontend dieser Anwendung ist unter folgendem Link vorzufinden: [climatelens_ui](https://github.com/cxconrad/climatelens_ui)

Die Dokumentation dieser Anwendung ist unter folgendem Link vorzufinden: [Dokumentation](./doc)

## Anwendung im Container starten
### Voraussetzung 
- Docker Version 4.37.1 oder höher
- Windows 11
### Anwendung starten (mit PowerShell)
```
cd ~;
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/FumiZwerg/ClimateLens-Backend/main/docker-compose.yml" -OutFile "docker-compose.yml";
docker compose up -d;
Start-Sleep -Seconds 60;
Start-Process "http://localhost:4173";
```
### Anwendung beenden (mit PowerShell)
```
cd ~;
docker compose down;
```