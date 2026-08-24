"""Reusable content-based recommender for the Phase 5 API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler, normalize
from sqlalchemy.orm import joinedload

from database.db.database import SessionLocal
from database.db.models import Track

FEATURE_COLUMNS = (
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
)


@dataclass(frozen=True)
class TrackResult:
    track_id: str
    track_name: str
    album_name: str | None
    artists: tuple[str, ...]
    genres: tuple[str, ...]
    popularity: int | None
    similarity: float | None = None


class SimilarityRecommender:
    def __init__(self) -> None:
        with SessionLocal() as session:
            self.tracks = (
                session.query(Track)
                .options(joinedload(Track.artists), joinedload(Track.genres))
                .all()
            )

        if not self.tracks:
            raise RuntimeError("The database contains no tracks. Run database/load_data.py first.")

        raw_features = np.array(
            [[getattr(track, column) for column in FEATURE_COLUMNS] for track in self.tracks],
            dtype=float,
        )
        medians = np.nanmedian(raw_features, axis=0)
        raw_features = np.where(np.isfinite(raw_features), raw_features, medians)
        self.matrix = normalize(StandardScaler().fit_transform(raw_features))
        self.by_id = {track.track_id: index for index, track in enumerate(self.tracks)}

    def search(self, query: str, limit: int) -> list[TrackResult]:
        normalized_query = query.strip().casefold()
        matches = []
        for track in self.tracks:
            artist_text = " ".join(artist.name for artist in track.artists)
            if normalized_query in track.track_name.casefold() or normalized_query in artist_text.casefold():
                matches.append(self._result(track))
                if len(matches) == limit:
                    break
        return matches

    def get_track(self, track_id: str) -> TrackResult | None:
        index = self.by_id.get(track_id)
        return None if index is None else self._result(self.tracks[index])

    def recommend(
        self,
        track_id: str,
        limit: int,
        genre: str | None = None,
        artist: str | None = None,
    ) -> list[TrackResult]:
        source_index = self.by_id.get(track_id)
        if source_index is None:
            return []

        scores = self.matrix @ self.matrix[source_index]
        candidate_indices = [index for index in range(len(self.tracks)) if index != source_index]
        if genre:
            genre_key = genre.casefold()
            candidate_indices = [
                index for index in candidate_indices
                if any(item.name.casefold() == genre_key for item in self.tracks[index].genres)
            ]
        if artist:
            artist_key = artist.casefold()
            candidate_indices = [
                index for index in candidate_indices
                if any(item.name.casefold() == artist_key for item in self.tracks[index].artists)
            ]

        ranked = sorted(candidate_indices, key=lambda index: scores[index], reverse=True)[:limit]
        return [self._result(self.tracks[index], float(scores[index])) for index in ranked]

    @staticmethod
    def _result(track: Track, similarity: float | None = None) -> TrackResult:
        return TrackResult(
            track_id=track.track_id,
            track_name=track.track_name,
            album_name=track.album_name,
            artists=tuple(item.name for item in track.artists),
            genres=tuple(item.name for item in track.genres),
            popularity=track.popularity,
            similarity=similarity,
        )


def database_path() -> Path:
    return Path(__file__).resolve().parent.parent / "similar_songs.db"
