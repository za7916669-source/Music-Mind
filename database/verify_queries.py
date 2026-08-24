"""
Phase 3 — Sanity-check queries against the loaded database.

Run this after load_data.py to confirm the schema and relationships work
as expected. These aren't unit tests, just a quick visual sanity check.
"""

from db.database import SessionLocal
from db.models import Track, Genre, Artist

session = SessionLocal()

print("=" * 60)
print("1. Total counts")
print("=" * 60)
print("Tracks:", session.query(Track).count())
print("Genres:", session.query(Genre).count())
print("Artists:", session.query(Artist).count())

print()
print("=" * 60)
print("2. A track that had multiple genres in the raw CSV (dedup check)")
print("=" * 60)
sample = None
for t in session.query(Track).limit(5000):
    if len(t.genres) > 1:
        sample = t
        break

if sample:
    print(f"Track: '{sample.track_name}' by {[a.name for a in sample.artists]}")
    print(f"Genres: {[g.name for g in sample.genres]}")
else:
    print("(no multi-genre track found in first 5000 rows — try increasing the scan limit)")

print()
print("=" * 60)
print("3. All tracks by a specific artist (collaboration handling)")
print("=" * 60)
artist = session.query(Artist).filter(Artist.name == "Bad Bunny").first()
if artist:
    print(f"Bad Bunny appears on {len(artist.tracks)} tracks, e.g.:")
    for t in artist.tracks[:5]:
        print(f"  - {t.track_name} (popularity {t.popularity})")

print()
print("=" * 60)
print("4. Top 5 most popular tracks in the 'k-pop' genre")
print("=" * 60)
kpop = session.query(Genre).filter(Genre.name == "k-pop").first()
if kpop:
    top_tracks = sorted(kpop.tracks, key=lambda t: t.popularity, reverse=True)[:5]
    for t in top_tracks:
        artists = ", ".join(a.name for a in t.artists)
        print(f"  {t.popularity:3d}  {t.track_name}  —  {artists}")

print()
print("=" * 60)
print("5. Sample feature vector for one track (what Phase 4 will consume)")
print("=" * 60)
sample_track = session.query(Track).first()
print(f"Track: {sample_track.track_name}")
print({
    "danceability": sample_track.danceability,
    "energy": sample_track.energy,
    "valence": sample_track.valence,
    "tempo": sample_track.tempo,
    "loudness": sample_track.loudness,
    "acousticness": sample_track.acousticness,
})

session.close()
