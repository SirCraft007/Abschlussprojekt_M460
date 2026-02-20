# Grade API Frontend

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
