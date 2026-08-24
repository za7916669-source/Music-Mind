# Phase 5 - Backend API

This FastAPI service exposes the Phase 4 similarity recommender over HTTP.

## Install

From the project root:

```powershell
pip install -r backend/requirements.txt
```

## Run

```powershell
uvicorn backend.main:app --reload
```

Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /health` - confirms the API is running and the SQLite database exists.
- `GET /tracks/search?q=Bad%20Bunny&limit=10` - searches track titles and artists.
- `GET /tracks/{track_id}` - returns one track.
- `GET /recommendations/{track_id}?limit=10` - returns similar tracks.
- Optional recommendation filters: `genre` and `artist`.

Example:

```powershell
curl "http://127.0.0.1:8000/tracks/search?q=Comedy&limit=3"
curl "http://127.0.0.1:8000/recommendations/5SuOikwiRyPMVoIQDJUgSV?limit=5"
```
