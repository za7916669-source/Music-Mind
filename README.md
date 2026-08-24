# 🎵 Music Mind

An AI-powered music recommendation system that helps users discover similar songs based on their audio features.

## ✨ Features

- 🔍 Search songs by title or artist
- 🎧 Find similar songs using AI
- 🧠 Content-based music recommendations
- ⚡ FastAPI backend
- ⚛️ React frontend
- 🗄️ SQLite database
- 🧪 Automated API testing

## 🧠 How It Works

Music Mind uses a content-based recommendation system.

Songs are represented using audio features such as:

- Danceability
- Energy
- Loudness
- Speechiness
- Acousticness
- Instrumentalness
- Liveness
- Valence
- Tempo
- Duration

The features are standardized and normalized. The system then uses cosine similarity to find songs with similar audio characteristics.

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

### Machine Learning
- NumPy
- Scikit-learn
- StandardScaler
- Cosine Similarity

### Frontend
- React
- Vite
- JavaScript

### Testing
- Pytest
- FastAPI TestClient

## 🏗️ Project Structure

```text
Music_Mind/
├── backend/              # FastAPI application and recommendation engine
├── database/             # Database models and data-loading scripts
├── frontend/             # React + Vite frontend
├── data/                 # Music dataset
├── notebooks/            # Data analysis and experimentation
├── backend/tests/        # API tests
├── similar_songs.db      # SQLite database
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md