import { useState } from "react";

import {
  searchTracks,
  getRecommendations,
} from "../services/api";

import TrackCard from "../components/TrackCard";

function Discover() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedTrack, setSelectedTrack] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const [recommendationLoading, setRecommendationLoading] =
    useState(false);


  async function handleSearch() {
    if (!searchQuery.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setRecommendations([]);
    setSelectedTrack(null);

    try {
      const data = await searchTracks(searchQuery);

      setResults(data.results || []);
    } catch (error) {
      console.error(error);

      setError(
        "Something went wrong while searching. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }


  function handleKeyDown(event) {
    if (event.key === "Enter") {
      handleSearch();
    }
  }


  function handleClearSearch() {
    setSearchQuery("");
    setResults([]);
    setRecommendations([]);
    setSelectedTrack(null);
    setError("");
  }


  async function handleTrackSelect(track) {
    setSelectedTrack(track);
    setRecommendations([]);
    setRecommendationLoading(true);
    setError("");

    try {
      const data = await getRecommendations(
        track.track_id
      );

      setRecommendations(data.results || []);
    } catch (error) {
      console.error(error);

      setError(
        "Could not load recommendations. Please try again."
      );
    } finally {
      setRecommendationLoading(false);
    }
  }


  return (
    <main className="discover-page">

      {/* =========================
          HERO
      ========================== */}

      <section className="hero">

        <div className="hero-overlay"></div>


        <div className="hero-content">

          <div className="hero-label">

            <span className="hero-label-dot"></span>

            AI-powered music discovery

          </div>


          <h1>
             Some songs don't just play.
            <br />
            <span>They stay with you.</span>
          </h1>


          <p>
             Find the next song to keep you in the moment.
          </p>



          {/* =========================
              SEARCH
          ========================== */}

          <div className="search-container">

            <div className="search-box">

              <span className="search-icon">
                🔎
              </span>


              <input
                type="text"
                placeholder="Search for a song or artist..."
                value={searchQuery}
                onChange={(event) =>
                  setSearchQuery(event.target.value)
                }
                onKeyDown={handleKeyDown}
              />


              {searchQuery && (
                <button
                  type="button"
                  className="clear-button"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                >
                  ×
                </button>
              )}


              <button
                type="button"
                className="search-button"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading ? "Searching..." : "Search"}
              </button>

            </div>


            <div className="search-hint">
              Press <kbd>Enter</kbd> to search
            </div>

          </div>

        </div>

      </section>


      {/* =========================
          ERROR
      ========================== */}

      {error && (
        <div className="message error-message">

          <span>!</span>

          {error}

        </div>
      )}


      {/* =========================
          LOADING
      ========================== */}

      {loading && (
        <section className="content-section">

          <div className="section-heading">

            <div>

              <span className="section-label">
                Searching
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


      {/* =========================
          SEARCH RESULTS
      ========================== */}

      {!loading && results.length > 0 && (

        <section className="content-section">

          <div className="section-heading">

            <div>

              <span className="section-label">
                Your results
              </span>

              <h2>
                Search Results
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
                onSelect={handleTrackSelect}
              />

            ))}

          </div>

        </section>

      )}


      {/* =========================
          NO RESULTS
      ========================== */}

      {!loading &&
        searchQuery &&
        results.length === 0 &&
        !error && (

          <section className="empty-state">

            <div className="empty-icon">
              🔎
            </div>

            <h2>
              No music found
            </h2>

            <p>
              Try searching for another song or artist.
            </p>

          </section>
        )}


      {/* =========================
          RECOMMENDATIONS
      ========================== */}

      {selectedTrack && (

        <section className="content-section recommendations-section">

          <div className="recommendation-header">

            <div>

              <span className="section-label">
                Music Mind AI
              </span>


              <h2>
                Similar to "{selectedTrack.track_name}"
              </h2>


              <p>
                Based on the musical characteristics
                of your selected track.
              </p>

            </div>


            <div className="ai-badge">
              ✦ AI Recommendations
            </div>

          </div>


          {/* SELECTED TRACK */}

          <div className="selected-track">

            <div className="selected-track-art">
              🎵
            </div>


            <div>

              <span className="selected-label">
                You selected
              </span>


              <h3>
                {selectedTrack.track_name}
              </h3>


              <p>
                {Array.isArray(selectedTrack.artists)
                  ? selectedTrack.artists.join(", ")
                  : selectedTrack.artists}
              </p>

            </div>

          </div>


          {/* RECOMMENDATION LOADING */}

          {recommendationLoading && (

            <div className="recommendation-loading">

              <div className="loading-spinner"></div>


              <div>

                <strong>
                  Finding similar songs...
                </strong>

                <p>
                  Music Mind is analyzing the track.
                </p>

              </div>

            </div>

          )}


          {/* RECOMMENDATIONS */}

          {!recommendationLoading &&
            recommendations.length > 0 && (

              <>

                <div className="recommendation-intro">

                  <span>✨</span>

                  <p>
                    We found {recommendations.length} songs
                    that share similar musical characteristics.
                  </p>

                </div>


                <div className="track-grid">

                  {recommendations.map((track) => (

                    <TrackCard
                      key={track.track_id}
                      track={track}
                      onSelect={handleTrackSelect}
                    />

                  ))}

                </div>

              </>
            )}


          {/* NO RECOMMENDATIONS */}

          {!recommendationLoading &&
            recommendations.length === 0 && (

              <div className="empty-state small">

                <div className="empty-icon">
                  🎧
                </div>

                <h2>
                  No similar songs found
                </h2>

                <p>
                  Try selecting another track.
                </p>

              </div>

            )}

        </section>

      )}

    </main>
  );
}

export default Discover;