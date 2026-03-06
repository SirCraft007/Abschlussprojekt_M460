# Grade API Frontend

# Einfachste verwendung online: 
https://noten.sercraft.ch

Noten selbst exportiern mit Chrome Extension: https://github.com/SirCraft007/schulnetz-plus

## Einrichtung

Starte den Server mit [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run flask run
```

## Debugging

Für die lokale Entwicklung kann der Flask-Server mit uv gestartet werden. Wenn die API ebenfalls lokal verfügbar ist, setze `debug=True` in `app.py`. Dann einfach:

```bash
uv run flask run --debug
```

## Locale API brauchen:


beide server starten aber auf unterschiedlichen ports

Dev url einstellen

```python
dev_url = True
```

Frontend auf 5000 (default)
```bash
uv run flask run --debug
```

API auf 5001
```bash
uv run flask run --port 5001 --debug
```