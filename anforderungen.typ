= Schulnetz+

== Kurzbeschreibung
#show link: underline

Eine HTMX APP für meine #link("https://api.sercraft.ch")[Noten API]. Mit Hilfe einer Chrome Extension können User ihre Noten in die API hochladen. In der CRUD-App können sie die Daten bearbeiten.

== Bewertungskriterien

+ Die Anwendung erlaubt es authentifizierten Benutzerinnen und Benutzern (JWT), ihre Noten in der App zu verwalten: Noten können erstellt, angezeigt, bearbeitet und gelöscht werden (vollständiges CRUD).

+ Die Anwendung kann Noten aus Schulnetz importieren, entweder automatisch oder durch Upload einer JSON-Datei, und speichert die importierten Noten in der Datenbank.

+ Die Anwendung berechnet aus den gespeicherten Noten automatisch die Pluspunkte sowie den Durchschnitt pro Fach und stellt diese Auswertungen übersichtlich dar.

#table(
  columns: 2,
  [*Datum*], [*Arbeit (bis zu diesem Termin abgeschlossen)*],
  table.cell(fill: orange)[*Di, 27.01.2026*],
  table.cell(
    fill: orange,
  )[Einlesen M460-8050\ API-Doku studieren\ Projektziel klar abgrenzen (Wrapper, kein Core-Backend)\ Flask-Projekt aufsetzen],
  table.cell(fill: orange)[*Fr, 30.01.2026*], table.cell(fill: orange)[API-Doku studieren\ Projectziehl konkretisieren],
  table.cell(fill: green)[*Sportferien*], table.cell(fill: green)[—],
  [*Di, 17.02.2026*], [Erste Verbindungstest\ Erste UI],
  [*Fr, 20.02.2026*], [Login Flow],
  [*Di, 24.02.2026*], [UI verbessern\ Display aller daten],
  [*Fr, 27.02.2026*], [Import aller noten von schulnetz],
  [*Di, 03.03.2026*], [UX-Feinschliff\ Puffer],
  [*Fr, 06.03.2026*], [Testing\ Doku (Architektur, Bewertungskriterien)\ *Abgabe 22:00*],
)

#highlight(
  fill: orange,
)[Krankheit]