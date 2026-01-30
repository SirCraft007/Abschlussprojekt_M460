= Schulnetz+

== Kurzbeschreibung
#show link: underline

Eine HTMX APP für meine #link("https://api.sercraft.ch")[Noten API]. Mit Hilfe einer Chrome Extension können User ihre Noten in die API hochladen. In der CRUD-App können sie die Daten bearbeiten.

== Bewertungskriterien

+ Volle CRUD Funktion
+ Import von Schulnetz (Automatisch oder als Upload von einer JSON-Datei)
+ Authentifizierung mit JWT
+ Ausrechnung der Pluspunkte und Fächerdurchschnitte
+ HTMX für einfachere Veränderung der UI

(Mehrere Bewertungskriterien da ich mir nicht sicher war was Sie am liebsten bewerten wollen)

#table(
  columns: 2,
  [*Datum*], [*Arbeit (bis zu diesem Termin abgeschlossen)*],
  [*Fr, 23.01.2026*],
  [Einlesen M460-8050\ API-Doku studieren\ Projektziel klar abgrenzen (Wrapper, kein Core-Backend)\ Flask-Projekt aufsetzen],

  [*Di, 27.01.2026*], [Anforderungen finalisieren\ Routen-Mapping API ↔ Flask\ Auth-Flow (JWT Weitergabe / Handling)],
  [*Fr, 30.01.2026*], [CRUD-Views mit HTMX (lesen + erstellen)\ Basis-Templates],
  [*Sportferien*], [—],
  [*Di, 17.02.2026*], [Vollständige CRUD-UI (HTMX)\ Fehler- & Ladezustände],
  [*Fr, 20.02.2026*], [Schulnetz-Import (JSON / API)\ Peer-Feedback einholen],
  [*Di, 24.02.2026*], [Feedback umsetzen\ Anzeige Pluspunkte & Durchschnitte],
  [*Fr, 27.02.2026*], [Chrome Extension: Upload → API\ End-to-End Flow getestet],
  [*Di, 03.03.2026*], [UX-Feinschliff\ Auth-Edge-Cases],
  [*Fr, 06.03.2026*], [Testing\ Doku (Architektur, Bewertungskriterien)\ *Abgabe 22:00*],
  [*Di, 10.03.2026*], [Puffer / Bugfix],
  [*Di, 17.03.2026*], [Kurzcheck Verstehen],
)

