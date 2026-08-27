"""
Music Mind - K-Means K Value Evaluation

Tests different numbers of clusters and compares:
- Inertia
- Silhouette Score

This script DOES NOT overwrite the existing trained model.

Run from the project root:

    python -m backend.ml.test_k_values
"""

from __future__ import annotations

import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

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

# K values we want to compare
K_VALUES = [5, 10, 15, 20, 25, 30, 40]


# ============================================================
# Load Tracks
# ============================================================

def load_tracks():
    """
    Load all tracks from the database.
    """

    with SessionLocal() as session:
        tracks = session.query(Track).all()

    if not tracks:
        raise RuntimeError(
            "The database contains no tracks."
        )

    return tracks


# ============================================================
# Prepare Features
# ============================================================

def prepare_features(tracks):
    """
    Extract and clean the numerical audio features.
    """

    raw_features = np.array(
        [
            [
                getattr(track, column)
                for column in FEATURE_COLUMNS
            ]
            for track in tracks
        ],
        dtype=float,
    )

    # Convert infinity values to NaN
    raw_features[~np.isfinite(raw_features)] = np.nan

    # Calculate median for each feature
    medians = np.nanmedian(
        raw_features,
        axis=0,
    )

    # Replace missing values with medians
    features = np.where(
        np.isnan(raw_features),
        medians,
        raw_features,
    )

    return features


# ============================================================
# Main Evaluation
# ============================================================

def main():

    print()
    print("========================================")
    print("     MUSIC MIND K-MEANS EVALUATION")
    print("========================================")

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print("\nLoading tracks...")

    tracks = load_tracks()

    print(
        f"Loaded {len(tracks):,} tracks."
    )

    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    print("\nPreparing features...")

    features = prepare_features(tracks)

    print(
        f"Feature matrix: {features.shape}"
    )

    # --------------------------------------------------------
    # Scale features
    # --------------------------------------------------------

    print("\nScaling features...")

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        features
    )

    print("Scaling complete.")

    # --------------------------------------------------------
    # Test K values
    # --------------------------------------------------------

    print("\nTesting K values...")

    results = []

    for k in K_VALUES:

        print()
        print("----------------------------------------")
        print(f"Testing K = {k}")
        print("----------------------------------------")

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        model.fit(scaled_features)

        # Inertia
        inertia = model.inertia_

        # Silhouette Score
        silhouette = silhouette_score(
            scaled_features,
            model.labels_,
            sample_size=min(
                10000,
                len(scaled_features),
            ),
            random_state=42,
        )

        results.append(
            {
                "k": k,
                "inertia": inertia,
                "silhouette": silhouette,
            }
        )

        print(
            f"Inertia:          {inertia:,.2f}"
        )

        print(
            f"Silhouette Score: {silhouette:.4f}"
        )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("========================================")
    print("             FINAL RESULTS")
    print("========================================")

    print()
    print(
        f"{'K':<8}"
        f"{'Inertia':<20}"
        f"{'Silhouette':<15}"
    )

    print("-" * 43)

    for result in results:

        print(
            f"{result['k']:<8}"
            f"{result['inertia']:<20,.2f}"
            f"{result['silhouette']:<15.4f}"
        )

    # --------------------------------------------------------
    # Best silhouette
    # --------------------------------------------------------

    best = max(
        results,
        key=lambda item: item["silhouette"],
    )

    print()
    print("========================================")
    print("BEST SILHOUETTE SCORE")
    print("========================================")

    print(
        f"K = {best['k']}"
    )

    print(
        f"Silhouette Score = "
        f"{best['silhouette']:.4f}"
    )

    print()
    print("Evaluation complete.")
    print()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()