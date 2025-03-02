# ADR 001: Einsatz von Python mit Django im Backend

## Datum
31. Januar 2025

## Status
Überholt

## Kontext
Das Team hat bereits umfangreiche Erfahrung mit Python und benötigt eine schnelle, einfache Lösung. Python bietet mit Django und Django REST Framework eine solide Grundlage für die schnelle Entwicklung von REST-APIs. Die Entscheidung für Python wurde auch getroffen, weil das Team wenig Erfahrung mit JavaScript hat, was zusätzlich längerfristige Einarbeitungszeit erfordert hätte.

## Entscheidung
Es wurde entschieden, Python zusammen mit Django und Django REST Framework für die Backend-Entwicklung zu verwenden. Die Entscheidung wurde aufgrund der bestehenden Python-Erfahrung im Team sowie der breiten Verfügbarkeit von Bibliotheken und der guten Dokumentation getroffen.

## Konsequenzen
**Positive:**

- Schnellere Entwicklung durch umfangreiche Dokumentation und Bibliotheken
- Hohe Wiederverwendbarkeit und Erweiterbarkeit durch Django
- Gute Unterstützung und Schulungsmöglichkeiten durch die große Community

**Negative:**

- Möglicherweise geringere Performance bei I/O Aufgaben (im Vergleich zu JavaScript)
- Integration mit Frontend-Technologien könnte zusätzliche Arbeit erfordern