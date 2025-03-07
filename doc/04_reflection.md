# Reflexion
### Kontext
Ziel im Rahmen dieses Projektes war die Entwicklung eines funktionierenden Backends für die Anwendung ClimateLens.

### Ziel der Reflexion
Ziel dieser Reflexion ist es, den Code und die Entwicklungsprozesse kritisch zu hinterfragen, Herausforderungen und Limitationen zu identifizieren und mögliche Lösungsansätze sowie technische Schulden zu analysieren.

### Herausforderungen
- **Datenintegration und -verarbeitung:** Unterschiedliche Datenformate und -quellen integrieren und verarbeiten 
- **Docker und Containerisierung:** Docker und docker-compose korrekt konfigurieren und auf verschiedenen Maschinen lauffähig machen
- **Fehlende Tests und Dokumentation:** Zu Beginn fehlende Tests und unzureichende Dokumentation

### Limitationen
- **Datenqualität und -konsistenz:** Externe Datenquellen mit ungewisser Qualität und Format
- **Performance bei hohem Datenvolumen:** Fehlendes Testing der Performance bei vielen Anfragen und Daten

### Lösungsansätze
- **Robustes Datenmodell und Tools:** Flexibles Modell, Pandas und NumPy für Datenverarbeitung
- **Standardisierte Docker-Umgebung:** Einheitliche Docker-Konfiguration und docker-compose
- **Caching:** Caching zur Lastreduzierung und Optimierung der Datenbankabfragen
- **Einführung von Unit-Tests und Dokumentation:** Tests für Stabilität und umfassende Dokumentation zur Wartbarkeit 

### Technische Schulden
- **Unzureichende Überprüfung der Datenqualität bei der Datenverarbeitung:** Aus der aktuell gegebenen Datenbasis ist nicht ersichtlich, ob die angeforderten Werte für einen bestimmten Zeitraum auch wirklich lückenlos vorhanden sind. Überprüfung der GHCN-inventory.txt auf valide Werte dementsprechend optimierungsbedürftig.
- **Error-Handling im Backend:** Fokus des Error-Handling lag primär im Frontend. Allerdings ist das für die zukünftige Weiterentwicklung keine technisch saubere Lösung.   

### Risiken
- **Abhängigkeit von externen Datenquellen:** Externe Quellen können ausfallen oder die Schnittstellen können sich ändern
- **Skalierungsprobleme bei wachsendem Datenvolumen:** Mögliche Performance-Probleme bei steigenden Daten und Anfragen

### Fazit
Die Entwicklung des ClimateLens-Backends war ein herausforderndes, aber lehrreiches Projekt, das die Wichtigkeit von Tests, Dokumentation und einer soliden Architektur verdeutlicht hat. Trotz der erkannten Risiken und technischen Schulden wurde das Backend erfolgreich implementiert, wobei noch Verbesserungspotential in Bereichen wie Skalierbarkeit, Errorhandling und Automatisierung besteht.
