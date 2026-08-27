"""
MusicMind Model Training

Creates the artifacts used by the recommendation engine:

    kmeans_model.joblib
    scaler.joblib
    genre_encoder.joblib
    metadata.joblib
    feature_matrix.npz
    track_ids.joblib
    cluster_labels.joblib

Feature representation:

    10 scaled audio features
    +
    weighted multi-label encoded genres

The recommender.py must use the exact same representation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Imports
# ============================================================

import joblib
import numpy as np

from scipy.sparse import csr_matrix, hstack, save_npz

from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler

from database.db.database import SessionLocal
from database.db.models import Track


# ============================================================
# Configuration
# ============================================================

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

GENRE_WEIGHT = 1.5

N_CLUSTERS = 20

RANDOM_STATE = 42


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "model"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

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

def safe_float(
    value,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.

    Invalid, missing, NaN, and infinite values
    are replaced with the default value.
    """

    try:
        number = float(value)

        if np.isfinite(number):
            return number

        return default

    except (TypeError, ValueError):
        return default


def get_genres(track: Track) -> list[str]:
    """
    Extract all genres belonging to a track.

    Returns a list such as:

        ["pop"]

    or:

        ["electronic", "dance"]

    MultiLabelBinarizer will convert these lists
    into a multi-hot encoded matrix.
    """

    genres = []

    for genre in track.genres:
        name = getattr(
            genre,
            "name",
            None,
        )

        if not name:
            continue

        name = name.strip().casefold()

        if name:
            genres.append(name)

    return sorted(set(genres))


# ============================================================
# Start
# ============================================================

print()
print("=" * 65)
print("MusicMind Model Training")
print("=" * 65)
print()


# ============================================================
# Load Tracks
# ============================================================

print("Loading tracks from database...")

with SessionLocal() as session:

    tracks = session.query(Track).all()

    # Force SQLAlchemy relationships to load
    # while the session is active.
    for track in tracks:
        list(track.genres)
        list(track.artists)


if not tracks:
    raise RuntimeError(
        "Database contains no tracks."
    )


print(
    f"Loaded {len(tracks):,} tracks."
)


# ============================================================
# Track IDs
# ============================================================

print()
print("Checking track IDs...")

track_ids = [
    track.track_id
    for track in tracks
]


if len(track_ids) != len(set(track_ids)):

    raise RuntimeError(
        "Duplicate track_id values found in database."
    )


print(
    f"Track IDs verified: {len(track_ids):,}"
)


# ============================================================
# Audio Matrix
# ============================================================

print()
print("Building audio matrix...")


audio_matrix = np.asarray(
    [
        [
            safe_float(
                getattr(
                    track,
                    column,
                    0.0,
                )
            )
            for column in FEATURE_COLUMNS
        ]
        for track in tracks
    ],
    dtype=np.float32,
)


print(
    f"Audio matrix: {audio_matrix.shape}"
)


# ============================================================
# Scale Audio Features
# ============================================================

print("Fitting StandardScaler...")


scaler = StandardScaler()


audio_scaled = scaler.fit_transform(
    audio_matrix
)


audio_scaled = np.asarray(
    audio_scaled,
    dtype=np.float32,
)


print(
    f"Scaled audio matrix: {audio_scaled.shape}"
)


# ============================================================
# Genres
# ============================================================

print()
print("Building genre data...")


genre_lists = [
    get_genres(track)
    for track in tracks
]


# Count tracks with no genres
tracks_without_genres = sum(
    1
    for genres in genre_lists
    if not genres
)


print(
    f"Tracks without genres: "
    f"{tracks_without_genres:,}"
)


# ============================================================
# Genre Encoder
# ============================================================

print("Fitting genre encoder...")


genre_encoder = MultiLabelBinarizer()


genre_matrix = genre_encoder.fit_transform(
    genre_lists
)


# Convert dense numpy matrix to sparse matrix.
genre_matrix = csr_matrix(
    genre_matrix,
    dtype=np.float32,
)


print(
    f"Genre matrix: {genre_matrix.shape}"
)


# ============================================================
# Genre Weight
# ============================================================

print(
    f"Applying genre weight: {GENRE_WEIGHT}"
)


genre_matrix = (
    genre_matrix * GENRE_WEIGHT
)


# ============================================================
# Combined Feature Matrix
# ============================================================

print()
print("Building final feature matrix...")


audio_sparse = csr_matrix(
    audio_scaled,
    dtype=np.float32,
)


feature_matrix = hstack(
    [
        audio_sparse,
        genre_matrix,
    ],
    format="csr",
)


print(
    f"Final feature matrix: "
    f"{feature_matrix.shape}"
)


# ============================================================
# K-Means
# ============================================================

print()
print(
    f"Training K-Means "
    f"with {N_CLUSTERS} clusters..."
)


kmeans = KMeans(
    n_clusters=N_CLUSTERS,
    random_state=RANDOM_STATE,
    n_init=10,
)


cluster_labels = kmeans.fit_predict(
    feature_matrix
)


print(
    "K-Means training complete."
)


# ============================================================
# Cluster Information
# ============================================================

unique_clusters, cluster_counts = np.unique(
    cluster_labels,
    return_counts=True,
)


print()
print("Cluster distribution:")


for cluster_id, count in zip(
    unique_clusters,
    cluster_counts,
):

    print(
        f"  Cluster {cluster_id:2d}: "
        f"{count:,} tracks"
    )


# ============================================================
# Save K-Means
# ============================================================

print()
print("Saving model...")


joblib.dump(
    kmeans,
    MODEL_PATH,
)


# ============================================================
# Save Scaler
# ============================================================

print("Saving scaler...")


joblib.dump(
    scaler,
    SCALER_PATH,
)


# ============================================================
# Save Genre Encoder
# ============================================================

print("Saving genre encoder...")


joblib.dump(
    genre_encoder,
    GENRE_ENCODER_PATH,
)


# ============================================================
# Save Feature Matrix
# ============================================================

print("Saving feature matrix...")


save_npz(
    FEATURE_MATRIX_PATH,
    feature_matrix,
)


# ============================================================
# Save Track IDs
# ============================================================

print("Saving track IDs...")


joblib.dump(
    track_ids,
    TRACK_IDS_PATH,
)


# ============================================================
# Save Cluster Labels
# ============================================================

print("Saving cluster labels...")


joblib.dump(
    cluster_labels,
    CLUSTER_LABELS_PATH,
)


# ============================================================
# Metadata
# ============================================================

genre_count = len(
    genre_encoder.classes_
)


metadata = {
    "feature_columns": list(
        FEATURE_COLUMNS
    ),

    "genre_weight": GENRE_WEIGHT,

    "audio_feature_count": len(
        FEATURE_COLUMNS
    ),

    "genre_feature_count": genre_count,

    "total_features": int(
        feature_matrix.shape[1]
    ),

    "n_clusters": N_CLUSTERS,

    "random_state": RANDOM_STATE,

    "track_count": len(tracks),

    "tracks_without_genres": tracks_without_genres,
}


joblib.dump(
    metadata,
    METADATA_PATH,
)


# ============================================================
# Complete
# ============================================================

print()
print("=" * 65)
print("MODEL TRAINING COMPLETE")
print("=" * 65)
print()


print(
    f"Tracks:          {len(tracks):,}"
)

print(
    f"Audio features:  {len(FEATURE_COLUMNS)}"
)

print(
    f"Genre features:  {genre_count}"
)

print(
    f"Total features:  {feature_matrix.shape[1]}"
)

print(
    f"Clusters:        {N_CLUSTERS}"
)

print()


print("Created:")

print(
    f"  {MODEL_PATH}"
)

print(
    f"  {SCALER_PATH}"
)

print(
    f"  {GENRE_ENCODER_PATH}"
)

print(
    f"  {METADATA_PATH}"
)

print(
    f"  {FEATURE_MATRIX_PATH}"
)

print(
    f"  {TRACK_IDS_PATH}"
)

print(
    f"  {CLUSTER_LABELS_PATH}"
)


print()
print("=" * 65)