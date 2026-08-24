import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from db.database import engine, SessionLocal, Base
from db.models import Track, Genre, Artist

BATCH_SIZE = 1000


def build_database(csv_path: str):
    print(f"Reading {csv_path} ...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df):,} rows.")

    # --- Step 1: collapse duplicate track_ids, collecting all genres per track ---
    print("Grouping duplicate track_ids and collecting genres ...")
    genre_map = df.groupby("track_id")["track_genre"].apply(lambda s: sorted(set(s))).to_dict()
    unique_tracks = df.drop_duplicates(subset="track_id", keep="first").copy()
    print(f"Reduced to {len(unique_tracks):,} unique tracks "
          f"({len(df) - len(unique_tracks):,} duplicate rows collapsed).")

    # --- Step 2: split artists on ';' ---
    unique_tracks["artist_list"] = unique_tracks["artists"].apply(
        lambda s: [a.strip() for a in str(s).split(";") if a.strip()]
    )

    # --- Step 3: create tables ---
    print("Creating tables (if they don't already exist) ...")
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()

    try:
        # --- Step 4: insert genres ---
        all_genre_names = sorted({g for genres in genre_map.values() for g in genres})
        print(f"Inserting {len(all_genre_names)} unique genres ...")
        genre_objs = {name: Genre(name=name) for name in all_genre_names}
        session.add_all(genre_objs.values())
        session.commit()

        # --- Step 5: insert artists ---
        all_artist_names = sorted({a for lst in unique_tracks["artist_list"] for a in lst})
        print(f"Inserting {len(all_artist_names)} unique artists ...")
        artist_objs = {}
        for i in range(0, len(all_artist_names), BATCH_SIZE):
            batch = all_artist_names[i:i + BATCH_SIZE]
            objs = [Artist(name=name) for name in batch]
            session.add_all(objs)
            session.commit()
            for obj in objs:
                artist_objs[obj.name] = obj
        print("Artists inserted.")

        # --- Step 6: insert tracks + link genres/artists ---
        print(f"Inserting {len(unique_tracks):,} tracks and linking relationships ...")
        rows = unique_tracks.to_dict(orient="records")

        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + BATCH_SIZE]
            for row in batch:
                track = Track(
                    track_id=row["track_id"],
                    track_name=row["track_name"],
                    album_name=row["album_name"],
                    popularity=row["popularity"],
                    duration_ms=row["duration_ms"],
                    explicit=bool(row["explicit"]),
                    danceability=row["danceability"],
                    energy=row["energy"],
                    key=row["key"],
                    loudness=row["loudness"],
                    mode=row["mode"],
                    speechiness=row["speechiness"],
                    acousticness=row["acousticness"],
                    instrumentalness=row["instrumentalness"],
                    liveness=row["liveness"],
                    valence=row["valence"],
                    tempo=row["tempo"],
                    time_signature=row["time_signature"],
                )
                track.genres = [genre_objs[g] for g in genre_map[row["track_id"]]]
                track.artists = [artist_objs[a] for a in row["artist_list"]]
                session.add(track)

            session.commit()
            done = min(i + BATCH_SIZE, len(rows))
            print(f"  {done:,} / {len(rows):,} tracks inserted", end="\r")

        print(f"\nDone. Database built at the location configured in db/database.py.")

    finally:
        session.close()


if __name__ == "__main__":
    default_csv = Path(__file__).resolve().parent.parent / "data" / "processed" / "cleaned_spotify_tracks.csv"
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else str(default_csv)
    build_database(csv_arg)
