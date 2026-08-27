"""
MusicMind FastAPI Backend

API for:

    - Track search
    - Track lookup
    - Similar-song recommendations
    - Health checks
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from backend.recommender import SimilarityRecommender


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = Path("similar_songs.db").resolve()

app = FastAPI(
    title="MusicMind Similar Songs API",
    version="1.0.0",
    description=(
        "Fast content-based music recommendation API "
        "using audio features and genre information."
    ),
)
@app.get("/debug/files")
def debug_files():
    return {
        "project_root": str(PROJECT_ROOT),
        "database_path": str(DATABASE_PATH),
        "database_exists": DATABASE_PATH.exists(),
        "database_size": (
            DATABASE_PATH.stat().st_size
            if DATABASE_PATH.exists()
            else None
        ),
        "root_files": [
            p.name
            for p in PROJECT_ROOT.iterdir()
        ],
    }



# ============================================================
# Response Models
# ============================================================

class TrackResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    track_id: str
    track_name: str
    album_name: str | None
    artists: list[str]
    genres: list[str]
    popularity: int | None
    similarity: float | None = None


class SearchResponse(BaseModel):

    query: str
    total_results: int
    results: list[TrackResponse]


class RecommendationResponse(BaseModel):

    seed_track_id: str
    genre: str | None
    artist: str | None
    total_results: int
    results: list[TrackResponse]


class HealthResponse(BaseModel):

    status: str
    database_exists: bool
    recommender_ready: bool


class APIInfoResponse(BaseModel):

    message: str
    version: str
    documentation: str


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="MusicMind Similar Songs API",
    version="1.0.0",
    description=(
        "Fast content-based music recommendation API "
        "using audio features and genre information."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# Recommender Singleton
# ============================================================

_recommender: SimilarityRecommender | None = None


def get_recommender() -> SimilarityRecommender:

    global _recommender

    if _recommender is None:

        print()
        print("=" * 65)
        print("Initializing MusicMind Recommendation Engine")
        print("=" * 65)
        print()

        _recommender = SimilarityRecommender()

        print()
        print(
            "Recommendation engine initialized successfully."
        )
        print()

    return _recommender


# ============================================================
# Response Conversion
# ============================================================

def to_response(
    track,
) -> TrackResponse:

    # --------------------------------------------------------
    # Artists
    # --------------------------------------------------------

    artists = []

    for artist in track.artists:

        name = getattr(
            artist,
            "name",
            None,
        )

        if name:
            artists.append(name)

    # --------------------------------------------------------
    # Genres
    # --------------------------------------------------------

    genres = []

    for genre in track.genres:

        name = getattr(
            genre,
            "name",
            None,
        )

        if name:
            genres.append(name)

    # --------------------------------------------------------
    # Popularity
    # --------------------------------------------------------

    popularity = getattr(
        track,
        "popularity",
        None,
    )

    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    similarity = getattr(
        track,
        "similarity",
        None,
    )

    return TrackResponse(
        track_id=track.track_id,

        track_name=track.track_name,

        album_name=getattr(
            track,
            "album_name",
            None,
        ),

        artists=artists,

        genres=genres,

        popularity=popularity,

        similarity=similarity,
    )


# ============================================================
# Root
# ============================================================

@app.get(
    "/",
    response_model=APIInfoResponse,
    tags=["System"],
)
def home():

    return APIInfoResponse(
        message=(
            "MusicMind Similar Songs API is running"
        ),

        version="1.0.0",

        documentation="/docs",
    )


# ============================================================
# Health
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health():

    # --------------------------------------------------------
    # Check actual database location
    # --------------------------------------------------------

    database_exists = DATABASE_PATH.exists()

    # --------------------------------------------------------
    # Check recommender
    # --------------------------------------------------------

    recommender_ready = False

    try:

        get_recommender()

        recommender_ready = True

    except Exception as error:

        print(
            f"Health check error: {error}"
        )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if (
        database_exists
        and recommender_ready
    ):

        status = "ok"

    else:

        status = "degraded"

    return HealthResponse(
        status=status,

        database_exists=database_exists,

        recommender_ready=recommender_ready,
    )


# ============================================================
# Search Tracks
# ============================================================

@app.get(
    "/tracks/search",
    response_model=SearchResponse,
    tags=["Tracks"],
)
def search_tracks(

    q: str = Query(
        min_length=1,

        description=(
            "Part of a track title or artist name"
        ),
    ),

    limit: int = Query(
        default=10,

        ge=1,

        le=50,
    ),
):

    query = q.strip()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not query:

        raise HTTPException(
            status_code=400,

            detail=(
                "Search query cannot be empty."
            ),
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    try:

        results = (
            get_recommender()
            .search(
                query=query,
                limit=limit,
            )
        )

    except Exception as error:

        print(
            f"Search error: {error}"
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Track search failed."
            ),
        )

    # --------------------------------------------------------
    # Convert
    # --------------------------------------------------------

    response_results = [
        to_response(track)
        for track in results
    ]

    return SearchResponse(
        query=query,

        total_results=len(
            response_results
        ),

        results=response_results,
    )


# ============================================================
# Get Single Track
# ============================================================

@app.get(
    "/tracks/{track_id}",
    response_model=TrackResponse,
    tags=["Tracks"],
)
def get_track(
    track_id: str,
):

    try:

        track = (
            get_recommender()
            .get_track(
                track_id
            )
        )

    except Exception as error:

        print(
            f"Track lookup error: {error}"
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Track lookup failed."
            ),
        )

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    if track is None:

        raise HTTPException(
            status_code=404,

            detail="Track not found.",
        )

    return to_response(
        track
    )


# ============================================================
# Recommendations
# ============================================================

@app.get(
    "/recommendations/{track_id}",
    response_model=RecommendationResponse,
    tags=["Recommendations"],
)
def recommendations(

    track_id: str,

    limit: int = Query(
        default=10,

        ge=1,

        le=50,
    ),

    genre: str | None = Query(
        default=None,
    ),

    artist: str | None = Query(
        default=None,
    ),
):

    # --------------------------------------------------------
    # Load recommender
    # --------------------------------------------------------

    try:

        recommender = get_recommender()

    except Exception as error:

        print(
            f"Recommender initialization error: {error}"
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Recommendation engine "
                "could not be initialized."
            ),
        )

    # --------------------------------------------------------
    # Verify seed track
    # --------------------------------------------------------

    try:

        seed_track = (
            recommender.get_track(
                track_id
            )
        )

    except Exception as error:

        print(
            f"Seed track lookup error: {error}"
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Unable to load seed track."
            ),
        )

    if seed_track is None:

        raise HTTPException(
            status_code=404,

            detail=(
                "Seed track not found."
            ),
        )

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    try:

        results = (
            recommender.recommend(

                track_id=track_id,

                limit=limit,

                genre=genre,

                artist=artist,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,

            detail=str(error),
        )

    except Exception as error:

        print(
            f"Recommendation error: {error}"
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "Recommendation generation failed."
            ),
        )

    # --------------------------------------------------------
    # Convert results
    # --------------------------------------------------------

    response_results = [
        to_response(track)
        for track in results
    ]

    return RecommendationResponse(

        seed_track_id=track_id,

        genre=genre,

        artist=artist,

        total_results=len(
            response_results
        ),

        results=response_results,
    )