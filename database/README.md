# Phase 3 — Database

Converts the cleaned Phase 1/2 CSV into a normalized SQL database, using SQLAlchemy so it works unchanged with SQLite now and PostgreSQL later.

## Schema

```
tracks ----< track_genres >---- genres
   |
   +-------< track_artists >---- artists
```

- **`tracks`** — one row per unique song (deduplicated on `track_id`). Holds all audio features (danceability, energy, tempo, etc.) plus metadata (name, album, popularity, duration).
- **`genres`** — one row per genre name.
- **`artists`** — one row per artist name (collaborations split out individually).
- **`track_genres`** / **`track_artists`** — many-to-many link tables.

### Why this shape (straight from Phase 2 findings)

- Phase 2 found **~24k rows were the same track repeated under different genre labels**. Storing genre as a plain column would have forced that duplication into the database. Instead, each track exists exactly once, linked to as many genres as it actually has.
- The `artists` column sometimes lists multiple collaborators (`"Bad Bunny;Jhayco"`). Splitting this into its own table means you can query "everything by this artist," including collaborations, without string-parsing at query time.
- Audio features stay directly on `tracks` (not their own table) because every track has exactly one value for each — splitting them out would just add unnecessary joins for Phase 4's similarity queries.

## Files

- `db/database.py` — engine/session setup. Change `DATABASE_URL` to switch from SQLite to PostgreSQL.
- `db/models.py` — the SQLAlchemy models (schema definition).
- `load_data.py` — ETL script: reads the CSV, dedupes, normalizes, populates the DB.
- `verify_queries.py` — sanity-check queries (counts, dedup check, artist lookup, genre lookup, sample feature vector).

## How to run

```bash
pip install sqlalchemy pandas
python load_data.py cleaned_spotify_tracks.csv
python verify_queries.py
```

This creates `similar_songs.db` (SQLite file) in the same folder.

## Verified results (from this dataset)

- 113,999 raw rows → **89,740 unique tracks**, 114 genres, 29,858 artists
- Dedup confirmed working: e.g. "Comedy" by Gen Hoshino correctly links to 4 genres (acoustic, j-pop, singer-songwriter, songwriter) as ONE track row, not four
- Artist collaboration lookups work: Bad Bunny → 129 tracks across all his features/collabs

## What Phase 4 will need from this DB

Phase 4 (ML Recommendation System) will pull each track's feature vector (danceability, energy, valence, tempo, loudness, acousticness, etc.) via `Track` objects, scale them, and compute similarity. The schema is already shaped for that — one row per track = one feature vector, with genre/artist available as optional filters (e.g. "similar songs, but only within this genre").
