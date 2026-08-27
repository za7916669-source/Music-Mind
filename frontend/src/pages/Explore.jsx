import { useState } from "react";

import { searchTracks } from "../services/api";
import TrackCard from "../components/TrackCard";

function Explore() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleExplore(searchTerm) {
    const finalQuery = searchTerm || query;

    if (!finalQuery.trim()) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      setQuery(finalQuery);

      const data = await searchTracks(finalQuery);

      setResults(data.results || []);
    } catch (error) {
      console.error(error);

      setError(
        "Something went wrong while exploring music."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      handleExplore();
    }
  }

  const genres = [
    {
      name: "Pop",
      description: "Modern hits & timeless favorites",
      icon: "✦",
    },
    {
      name: "Rock",
      description: "Guitars, energy & attitude",
      icon: "◈",
    },
    {
      name: "Hip-Hop",
      description: "Beats, rhythm & flow",
      icon: "◆",
    },
    {
      name: "Electronic",
      description: "Electronic sounds & movement",
      icon: "⌁",
    },
    {
      name: "Jazz",
      description: "Smooth, expressive & timeless",
      icon: "◌",
    },
    {
      name: "Classical",
      description: "Orchestral & beautiful compositions",
      icon: "♫",
    },
  ];

  return (
    <main className="explore-page">

      {/* ==================================================
          HERO
      ================================================== */}

      <section className="explore-hero">

        <div className="explore-hero-glow"></div>

        <div className="explore-hero-content">

          <div className="explore-label">

            <span className="explore-label-dot"></span>

            Explore the MusicMind library

          </div>


          <h1>
            There's always
            <br />
            <span>something to discover.</span>
          </h1>


          <p>
            Search through thousands of tracks by genre,
            artist, or song. Let MusicMind help you find
            something worth listening to.
          </p>


          {/* SEARCH */}

          <div className="explore-search-container">

            <div className="explore-search-box">

              <span className="explore-search-icon">
                🔎
              </span>


              <input
                type="text"
                placeholder="Search for a song, artist, or genre..."
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                onKeyDown={handleKeyDown}
              />


              {query && (
                <button
                  type="button"
                  className="explore-clear-button"
                  onClick={() => {
                    setQuery("");
                    setResults([]);
                    setError("");
                  }}
                  aria-label="Clear search"
                >
                  ×
                </button>
              )}


              <button
                type="button"
                className="explore-search-button"
                onClick={() => handleExplore()}
                disabled={loading}
              >
                {loading ? "Searching..." : "Explore"}
              </button>

            </div>


            <div className="explore-search-hint">
              Press <kbd>Enter</kbd> to explore
            </div>

          </div>

        </div>

      </section>


      {/* ==================================================
          ERROR
      ================================================== */}

      {error && (
        <div className="message error-message">

          <span>!</span>

          {error}

        </div>
      )}


      {/* ==================================================
          GENRES
      ================================================== */}

      <section className="explore-content">

        <div className="explore-section-heading">

          <div>

            <span className="section-label">
              Explore by mood
            </span>

            <h2>
              Start with a genre
            </h2>

          </div>

          <span className="explore-section-description">
            Pick a sound and see where it takes you.
          </span>

        </div>


        <div className="genre-grid">

          {genres.map((genre) => (

            <button
              type="button"
              key={genre.name}
              className="genre-card"
              onClick={() => handleExplore(genre.name)}
              disabled={loading}
            >

              <div className="genre-card-icon">
                {genre.icon}
              </div>


              <div className="genre-card-content">

                <h3>
                  {genre.name}
                </h3>

                <p>
                  {genre.description}
                </p>

              </div>


              <span className="genre-card-arrow">
                →
              </span>

            </button>

          ))}

        </div>

      </section>


      {/* ==================================================
          LOADING
      ================================================== */}

      {loading && (

        <section className="explore-content">

          <div className="explore-section-heading">

            <div>

              <span className="section-label">
                MusicMind
              </span>

              <h2>
                Finding your music...
              </h2>

            </div>

          </div>


          <div className="loading-grid">

            {[1, 2, 3, 4].map((item) => (

              <div
                className="skeleton-card"
                key={item}
              >

                <div className="skeleton-art"></div>

                <div className="skeleton-lines">

                  <div></div>
                  <div></div>
                  <div></div>

                </div>

              </div>

            ))}

          </div>

        </section>

      )}


      {/* ==================================================
          RESULTS
      ================================================== */}

      {!loading && results.length > 0 && (

        <section className="explore-content explore-results">

          <div className="explore-section-heading">

            <div>

              <span className="section-label">
                Explore results
              </span>

              <h2>
                {query
                  ? `Results for "${query}"`
                  : "Explore Music"}
              </h2>

            </div>


            <span className="result-count">
              {results.length} tracks
            </span>

          </div>


          <div className="track-grid">

            {results.map((track) => (

              <TrackCard
                key={track.track_id}
                track={track}
              />

            ))}

          </div>

        </section>

      )}


      {/* ==================================================
          EMPTY STATE
      ================================================== */}

      {!loading &&
        query &&
        results.length === 0 &&
        !error && (

          <section className="explore-empty">

            <div className="empty-icon">
              🎧
            </div>

            <h2>
              Nothing found
            </h2>

            <p>
              We couldn't find tracks matching "{query}".
              Try another song, artist, or genre.
            </p>

            <button
              type="button"
              onClick={() => {
                setQuery("");
                setResults([]);
              }}
            >
              Explore something else
            </button>

          </section>

        )}

    </main>
  );
}

export default Explore;