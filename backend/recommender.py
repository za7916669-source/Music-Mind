"""
MusicMind Recommendation Engine

Fast content-based recommendation system.

Training creates:

    feature_matrix.npz
    track_ids.joblib
    cluster_labels.joblib
    kmeans_model.joblib
    scaler.joblib
    genre_encoder.joblib
    metadata.joblib

The backend loads these artifacts directly.

Recommendation flow:

    1. Find seed track.
    2. Get its precomputed feature vector.
    3. Find nearest songs using cosine distance.
    4. Remove the seed track and duplicate releases.
    5. Apply optional genre / artist filters.
    6. Return the best matches.

Search flow:

    1. Search track titles directly in SQLite.
    2. Search artists through the many-to-many relationship.
    3. Order results by popularity.
    4. Return only the requested number of tracks.

The expensive feature construction is performed during
model training. The recommendation engine loads the
already-created feature matrix.
"""

from __future__ import annotations

from pathlib import Path

import joblib

from scipy.sparse import load_npz
from sklearn.neighbors import NearestNeighbors

from database.db.database import SessionLocal
from database.db.models import Track, Artist


# ============================================================
# Configuration
# ============================================================

MAX_LIMIT = 50

SEARCH_NEIGHBORS = 250


# ============================================================
# Paths
# ============================================================

# recommender.py:
#
#     backend/recommender.py
#
# Model files:
#
#     backend/ml/model/
#

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "ml" / "model"

MODEL_PATH = MODEL_DIR / "kmeans_model.joblib"
SCALER_PATH = MODEL_DIR / "scaler.joblib"
GENRE_ENCODER_PATH = MODEL_DIR / "genre_encoder.joblib"
METADATA_PATH = MODEL_DIR / "metadata.joblib"

FEATURE_MATRIX_PATH = MODEL_DIR / "feature_matrix.npz"
TRACK_IDS_PATH = MODEL_DIR / "track_ids.joblib"
CLUSTER_LABELS_PATH = MODEL_DIR / "cluster_labels.joblib"


# ============================================================
# Helpers
# ============================================================

def get_track_artists(track: Track) -> list[str]:

    artists = []

    for artist in track.artists:

        name = getattr(
            artist,
            "name",
            None,
        )

        if not name:
            continue

        name = name.strip()

        if name:
            artists.append(name)

    return artists


def get_track_genres(track: Track) -> list[str]:

    genres = []

    for genre in track.genres:

        name = getattr(
            genre,
            "name",
            None,
        )

        if not name:
            continue

        name = name.strip()

        if name:
            genres.append(name)

    return sorted(set(genres))


def normalize(value) -> str:

    if value is None:
        return ""

    return str(value).strip().casefold()


def create_song_key(track: Track) -> tuple:

    """
    Creates a normalized identity for a song.

    Used to prevent duplicate releases of the
    same song from appearing multiple times.
    """

    track_name = normalize(
        track.track_name
    )

    artist_names = tuple(
        sorted(
            normalize(name)
            for name in get_track_artists(track)
        )
    )

    return (
        track_name,
        artist_names,
    )


# ============================================================
# Recommendation Engine
# ============================================================

class SimilarityRecommender:

    def __init__(self):

        print(
            "Loading MusicMind recommender..."
        )

        # ----------------------------------------------------
        # Validate artifacts
        # ----------------------------------------------------

        required_files = [
            MODEL_PATH,
            SCALER_PATH,
            GENRE_ENCODER_PATH,
            METADATA_PATH,
            FEATURE_MATRIX_PATH,
            TRACK_IDS_PATH,
            CLUSTER_LABELS_PATH,
        ]

        for path in required_files:

            if not path.exists():

                raise FileNotFoundError(
                    f"Required recommendation artifact "
                    f"not found:\n{path}\n\n"
                    f"Run train_model.py first."
                )

        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        print(
            "Loading metadata..."
        )

        self.metadata = joblib.load(
            METADATA_PATH
        )

        # ----------------------------------------------------
        # Load feature matrix
        # ----------------------------------------------------

        print(
            "Loading saved feature matrix..."
        )

        self.feature_matrix = load_npz(
            FEATURE_MATRIX_PATH
        ).tocsr()

        # ----------------------------------------------------
        # Load track IDs
        # ----------------------------------------------------

        print(
            "Loading track IDs..."
        )

        self.track_ids = joblib.load(
            TRACK_IDS_PATH
        )

        # ----------------------------------------------------
        # Load cluster labels
        # ----------------------------------------------------

        print(
            "Loading cluster labels..."
        )

        self.cluster_labels = joblib.load(
            CLUSTER_LABELS_PATH
        )

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        row_count = self.feature_matrix.shape[0]

        if len(self.track_ids) != row_count:

            raise RuntimeError(
                "Feature matrix and track IDs have "
                "different numbers of rows."
            )

        if len(self.cluster_labels) != row_count:

            raise RuntimeError(
                "Feature matrix and cluster labels have "
                "different numbers of rows."
            )

        # ----------------------------------------------------
        # Validate feature dimensions
        # ----------------------------------------------------

        expected_features = self.metadata.get(
            "total_features"
        )

        actual_features = self.feature_matrix.shape[1]

        if (
            expected_features is not None
            and actual_features != expected_features
        ):

            raise RuntimeError(
                "Feature matrix dimension does not "
                "match training metadata.\n"
                f"Expected: {expected_features}\n"
                f"Actual:   {actual_features}"
            )

        # ----------------------------------------------------
        # Load model artifacts
        # ----------------------------------------------------

        print(
            "Loading trained model artifacts..."
        )

        self.kmeans = joblib.load(
            MODEL_PATH
        )

        self.scaler = joblib.load(
            SCALER_PATH
        )

        self.genre_encoder = joblib.load(
            GENRE_ENCODER_PATH
        )

        # ----------------------------------------------------
        # Track index
        # ----------------------------------------------------

        self.track_index = {
            track_id: index
            for index, track_id
            in enumerate(self.track_ids)
        }

        # ----------------------------------------------------
        # Nearest Neighbor Search
        # ----------------------------------------------------

        print(
            "Preparing similarity search..."
        )

        self.nearest_neighbors = NearestNeighbors(
            metric="cosine",
            algorithm="brute",
            n_neighbors=min(
                SEARCH_NEIGHBORS,
                row_count,
            ),
        )

        self.nearest_neighbors.fit(
            self.feature_matrix
        )

        # ----------------------------------------------------
        # Ready
        # ----------------------------------------------------

        print(
            f"Loaded {len(self.track_ids):,} tracks."
        )

        print(
            f"Feature matrix: "
            f"{self.feature_matrix.shape}"
        )

        print(
            f"Audio features: "
            f"{self.metadata.get('audio_feature_count', 'unknown')}"
        )

        print(
            f"Genre features: "
            f"{self.metadata.get('genre_feature_count', 'unknown')}"
        )

        print(
            f"Clusters: "
            f"{self.metadata.get('n_clusters', 'unknown')}"
        )

        print(
            "Recommendation engine ready."
        )

    # ========================================================
    # Get Track
    # ========================================================

    def get_track(
        self,
        track_id: str,
    ) -> Track | None:

        with SessionLocal() as session:

            track = (
                session.query(Track)
                .filter(
                    Track.track_id == track_id
                )
                .first()
            )

            if track is None:
                return None

            # Load relationships before session closes.
            list(track.genres)
            list(track.artists)

            return track

    # ========================================================
    # Search
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Track]:

        query = normalize(query)

        if not query:
            return []

        # ----------------------------------------------------
        # Validate limit
        # ----------------------------------------------------

        try:

            limit = int(limit)

        except (
            TypeError,
            ValueError,
        ):

            limit = 10

        limit = max(
            1,
            min(
                limit,
                MAX_LIMIT,
            ),
        )

        search_pattern = f"%{query}%"

        with SessionLocal() as session:

            # ------------------------------------------------
            # Search track titles first.
            # ------------------------------------------------

            title_results = (
                session.query(Track)
                .filter(
                    Track.track_name.ilike(
                        search_pattern
                    )
                )
                .order_by(
                    Track.popularity.desc()
                )
                .limit(limit)
                .all()
            )

            # Load relationships before session closes.
            for track in title_results:

                list(track.genres)
                list(track.artists)

            # If title search already filled the limit,
            # there is no need to search artists.
            if len(title_results) >= limit:

                return title_results

            # ------------------------------------------------
            # Search artists directly in the database.
            # ------------------------------------------------

            existing_ids = {
                track.track_id
                for track in title_results
            }

            remaining = (
                limit - len(title_results)
            )

            artist_results = (
                session.query(Track)
                .join(Track.artists)
                .filter(
                    ~Track.track_id.in_(
                        existing_ids
                    )
                )
                .filter(
                    Artist.name.ilike(
                        search_pattern
                    )
                )
                .order_by(
                    Track.popularity.desc()
                )
                .limit(remaining)
                .all()
            )

            # Load relationships before session closes.
            for track in artist_results:

                list(track.genres)
                list(track.artists)

            # ------------------------------------------------
            # Combine results.
            # ------------------------------------------------

            return (
                title_results
                + artist_results
            )

    # ========================================================
    # Recommendation
    # ========================================================

    def recommend(
        self,
        track_id: str,
        limit: int = 10,
        genre: str | None = None,
        artist: str | None = None,
    ) -> list[Track]:

        # ----------------------------------------------------
        # Find seed index
        # ----------------------------------------------------

        seed_index = self.track_index.get(
            track_id
        )

        if seed_index is None:

            raise ValueError(
                f"Track '{track_id}' was not found."
            )

        # ----------------------------------------------------
        # Validate limit
        # ----------------------------------------------------

        try:

            limit = int(limit)

        except (
            TypeError,
            ValueError,
        ):

            limit = 10

        limit = max(
            1,
            min(
                limit,
                MAX_LIMIT,
            ),
        )

        genre_filter = normalize(
            genre
        )

        artist_filter = normalize(
            artist
        )

        # ----------------------------------------------------
        # Get seed track
        # ----------------------------------------------------

        seed_track = self.get_track(
            track_id
        )

        if seed_track is None:

            raise ValueError(
                f"Track '{track_id}' was not found."
            )

        # ----------------------------------------------------
        # Create seed identity
        # ----------------------------------------------------

        seed_song_key = create_song_key(
            seed_track
        )

        # ----------------------------------------------------
        # Query nearest songs
        # ----------------------------------------------------

        neighbor_count = min(
            max(
                SEARCH_NEIGHBORS,
                limit * 10,
            ),
            self.feature_matrix.shape[0],
        )

        distances, indices = (
            self.nearest_neighbors.kneighbors(
                self.feature_matrix[
                    seed_index
                ],
                n_neighbors=neighbor_count,
            )
        )

        distances = distances[0]
        indices = indices[0]

        # ----------------------------------------------------
        # Prepare candidates
        # ----------------------------------------------------

        candidate_ids = []

        for distance, index in zip(
            distances,
            indices,
        ):

            index = int(index)

            # Skip exact seed row.
            if index == seed_index:
                continue

            candidate_ids.append(
                (
                    index,
                    float(distance),
                )
            )

        if not candidate_ids:
            return []

        # ----------------------------------------------------
        # Fetch candidate tracks
        # ----------------------------------------------------

        candidate_track_ids = [
            self.track_ids[index]
            for index, _
            in candidate_ids
        ]

        with SessionLocal() as session:

            tracks = (
                session.query(Track)
                .filter(
                    Track.track_id.in_(
                        candidate_track_ids
                    )
                )
                .all()
            )

            track_by_id = {
                track.track_id: track
                for track in tracks
            }

            results = []

            seen_song_keys = set()

            # ------------------------------------------------
            # Preserve nearest-neighbor order.
            # ------------------------------------------------

            for (
                index,
                distance,
            ) in candidate_ids:

                candidate_id = (
                    self.track_ids[index]
                )

                candidate = track_by_id.get(
                    candidate_id
                )

                if candidate is None:
                    continue

                # --------------------------------------------
                # Load relationships.
                # --------------------------------------------

                list(candidate.genres)
                list(candidate.artists)

                # --------------------------------------------
                # Create candidate identity.
                # --------------------------------------------

                candidate_song_key = (
                    create_song_key(
                        candidate
                    )
                )

                # --------------------------------------------
                # Never recommend another release of
                # the exact same song and artist.
                # --------------------------------------------

                if candidate_song_key == seed_song_key:
                    continue

                # --------------------------------------------
                # Genre filter.
                # --------------------------------------------

                if genre_filter:

                    candidate_genres = {
                        normalize(name)
                        for name in get_track_genres(
                            candidate
                        )
                    }

                    if genre_filter not in candidate_genres:
                        continue

                # --------------------------------------------
                # Artist filter.
                # --------------------------------------------

                if artist_filter:

                    candidate_artists = {
                        normalize(name)
                        for name in get_track_artists(
                            candidate
                        )
                    }

                    if not any(
                        artist_filter in artist_name
                        for artist_name in candidate_artists
                    ):
                        continue

                # --------------------------------------------
                # Remove duplicate releases.
                # --------------------------------------------

                if candidate_song_key in seen_song_keys:
                    continue

                seen_song_keys.add(
                    candidate_song_key
                )

                # --------------------------------------------
                # Convert cosine distance to UI score.
                # --------------------------------------------

                similarity = self._similarity_score(
                    distance
                )

                candidate.similarity = similarity

                results.append(
                    candidate
                )

                if len(results) >= limit:
                    break

            return results

    # ========================================================
    # Similarity Score
    # ========================================================

    @staticmethod
    def _similarity_score(
        cosine_distance: float,
    ) -> float:

        """
        Convert cosine distance into a UI score.

        This is a similarity score for display purposes,
        NOT a probability or confidence percentage.
        """

        score = (
            100.0
            * (1.0 - cosine_distance)
        )

        score = max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

        return round(
            score,
            1,
        )

    # ========================================================
    # Compatibility Method
    # ========================================================

    def get_recommendations(
        self,
        track_id: str,
        limit: int = 10,
        genre=None,
        artist=None,
    ) -> list[Track]:

        return self.recommend(
            track_id=track_id,
            limit=limit,
            genre=genre,
            artist=artist,
        )


# ============================================================
# Singleton
# ============================================================

_recommender = None


def get_recommender() -> SimilarityRecommender:

    global _recommender

    if _recommender is None:

        _recommender = SimilarityRecommender()

    return _recommender