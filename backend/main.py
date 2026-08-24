"""FastAPI application for Similar Songs AI."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from backend.recommender import SimilarityRecommender, database_path


# ============================================================
# Response Models
# ============================================================

class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class APIInfoResponse(BaseModel):
    message: str
    version: str
    documentation: str


# ============================================================
# Recommender
# ============================================================

@lru_cache(maxsize=1)
def get_recommender() -> SimilarityRecommender:
    """
    Create the recommendation engine once and reuse it.

    This prevents the recommender from being reloaded
    for every API request.
    """
    return SimilarityRecommender()


# ============================================================
# Helper Functions
# ============================================================

def to_response(track) -> TrackResponse:
    """
    Convert a track returned by the recommender
    into a validated API response.
    """
    return TrackResponse(
        track_id=track.track_id,
        track_name=track.track_name,
        album_name=track.album_name,
        artists=list(track.artists),
        genres=list(track.genres),
        popularity=track.popularity,
        similarity=track.similarity,
    )


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="MusicMind Similar Songs API",
    version="1.0.0",
    description=(
        "A content-based music recommendation API. "
        "Songs are recommended using audio-feature similarity."
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
# Root Endpoint
# ============================================================

@app.get("/", response_model=APIInfoResponse, tags=["System"])
def home() -> APIInfoResponse:
    """
    Welcome endpoint for the MusicMind API.
    """
    return APIInfoResponse(
        message="MusicMind Similar Songs API is running",
        version="1.0.0",
        documentation="/docs",
    )


# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health() -> HealthResponse:
    """
    Check whether the API and database are available.
    """
    return HealthResponse(
        status="ok",
        database_exists=database_path().exists(),
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
        description="Part of a track title or artist name",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    ),
) -> SearchResponse:
    """
    Search for tracks by track title or artist name.
    """

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    results = get_recommender().search(query, limit)

    response_results = [
        to_response(track)
        for track in results
    ]

    return SearchResponse(
        query=query,
        total_results=len(response_results),
        results=response_results,
    )


# ============================================================
# Get Track by ID
# ============================================================

@app.get(
    "/tracks/{track_id}",
    response_model=TrackResponse,
    tags=["Tracks"],
)
def get_track(track_id: str) -> TrackResponse:
    """
    Get one track using its Spotify track ID.
    """

    track = get_recommender().get_track(track_id)

    if track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    return to_response(track)


# ============================================================
# Get Similar Songs
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
        description="Maximum number of recommendations",
    ),
    genre: str | None = Query(
        default=None,
        description="Optional genre filter",
    ),
    artist: str | None = Query(
        default=None,
        description="Optional artist filter",
    ),
) -> RecommendationResponse:
    """
    Get similar songs using the AI recommendation engine.

    Recommendations are generated from audio-feature similarity.
    """

    recommender = get_recommender()

    seed_track = recommender.get_track(track_id)

    if seed_track is None:
        raise HTTPException(
            status_code=404,
            detail="Seed track not found",
        )

    results = recommender.recommend(
        track_id,
        limit,
        genre=genre,
        artist=artist,
    )

    response_results = [
        to_response(track)
        for track in results
    ]

    return RecommendationResponse(
        seed_track_id=track_id,
        genre=genre,
        artist=artist,
        total_results=len(response_results),
        results=response_results,
    )