# ADR 002: Einsatz von Python mit FastAPI im Backend

## Datum
14. Februar 2025

## Status
Akzeptiert

## Kontext
Das ClimateLens-Projekt ist ein kleines Universitätsprojekt, bei dem eine benutzerfreundliche, leicht verständliche Programmiersprache sowie eine schnelle und moderne API benötigt werden. Die Hauptanforderungen lauten:

- **Schnelle Entwicklung:** Die Lösung soll zügig und produktiv umsetzbar sein
- **Einfache API-Integration:** Eine unkomplizierte Kommunikation über ein REST-Backend ist essenziell
- **Wartbarkeit & Erweiterbarkeit:** Die Architektur muss zukünftige Erweiterungen und Wartungsarbeiten unterstützen

Während der Entwicklung mit Django wurde festgestellt, dass das Framework-Setup sehr aufwendig ist und die umfangreichen Funktionen und Features von Django für unseren spezifischen Use-Case größtenteils überflüssig sind. Aufgrund dessen haben wir uns entschieden, FastAPI statt Django zu verwenden, da es eine leichtere und schnellere Alternative bietet, die besser zu unseren Anforderungen passt. FastAPI ermöglicht eine zügigere Entwicklung und ist besonders gut geeignet, wenn es um eine einfache und effiziente API-Integration geht, ohne die Komplexität eines größeren Frameworks wie Django.

## Entscheidung
Für das Backend wird **Python** als Programmiersprache gewählt – in Kombination mit dem asynchronen Web-Framework **FastAPI**. Zur Ausführung und Bereitstellung kommen weitere Technologien zum Einsatz:

- **uvicorn:** ASGI-Server zur Ausführung der FastAPI-Anwendung
- **Docker & docker-compose:** Containerisierung und einfache Bereitstellung der Anwendung
- **Zusätzliche Python-Bibliotheken:** Gemäß den Anforderungen (siehe [requirements.txt](../requirements.txt) im Repository)

Die Entscheidung fiel zugunsten von Python und FastAPI, da:

- Python eine klare, leicht verständliche Syntax bietet, was die schnelle Entwicklung unterstützt
- FastAPI native Unterstützung für asynchrone Programmierung bereitstellt
- Die Kombination beider Technologien eine gute Balance zwischen Entwicklungsproduktivität und Performance ermöglicht

## Konsequenzen
**Positive:**
- Schnelle Entwicklung und gutes Onboarding dank Python und FastAPI
- Viele Updates und Unterstützung durch die Python- und FastAPI-Community
- Einfache Integration von Unit-Tests und Mocking

**Negative:**
- Möglicherweise geringere Performance bei I/O Aufgaben (im Vergleich zu JavaScript)
- Abhängigkeit von Drittanbieter-Bibliotheken erfordert regelmäßige Updates und Sicherheitschecks
