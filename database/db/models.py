"""
Database schema for the Similar Songs AI project.

Design decisions (based directly on Phase 2 EDA findings):

1. DEDUPLICATION: Phase 2 found ~24k rows in the raw CSV are the same physical
   track repeated under different genre labels. Instead of storing genre as a
   plain column on `tracks` (which would force duplicate track rows again),
   genre is pulled into its own table and linked via a many-to-many
   relationship (`track_genres`). Each track now exists exactly ONCE in the
   `tracks` table, and can be linked to multiple genres.

2. ARTISTS: the raw `artists` column sometimes contains multiple artists
   separated by semicolons (e.g. "Bad Bunny;Jhayco"). This is normalized the
   same way as genre — an `artists` table plus a `track_artists` link table —
   so you can query "all tracks by this artist" cleanly, including
   collaborations, without string parsing at query time.

3. AUDIO FEATURES stay as columns directly on `tracks` (not a separate table)
   because every track has exactly one value for each — a one-to-one
   relationship gains nothing from being split out, and keeping them together
   makes the similarity queries in Phase 4 simpler (one row per track = one
   feature vector).
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, Table
)
from sqlalchemy.orm import relationship
from .database import Base

# --- Association (many-to-many) tables --------------------------------------

track_genres = Table(
    "track_genres",
    Base.metadata,
    Column("track_id", String, ForeignKey("tracks.track_id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

track_artists = Table(
    "track_artists",
    Base.metadata,
    Column("track_id", String, ForeignKey("tracks.track_id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)


# --- Core tables -------------------------------------------------------------

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)

    tracks = relationship("Track", secondary=track_genres, back_populates="genres")

    def __repr__(self):
        return f"<Genre {self.name}>"


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)

    tracks = relationship("Track", secondary=track_artists, back_populates="artists")

    def __repr__(self):
        return f"<Artist {self.name}>"


class Track(Base):
    __tablename__ = "tracks"

    # Spotify's own ID, used directly as the primary key (already unique per song).
    track_id = Column(String, primary_key=True)

    track_name = Column(String, nullable=False, index=True)
    album_name = Column(String)

    # Metadata
    popularity = Column(Integer)
    duration_ms = Column(Integer)
    explicit = Column(Boolean)

    # Audio features (Phase 2 confirmed these need scaling before similarity —
    # that scaling happens at query time in Phase 4, raw values are kept here)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Integer)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Integer)

    # Relationships
    genres = relationship("Genre", secondary=track_genres, back_populates="tracks")
    artists = relationship("Artist", secondary=track_artists, back_populates="tracks")

    def __repr__(self):
        return f"<Track {self.track_name}>"
