import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getRecommendations } from "../services/api";
import TrackCard from "../components/TrackCard";


function Song() {
  const location = useLocation();
  const navigate = useNavigate();

  const track = location.state?.track;

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  useEffect(() => {
    if (!track) {
      return;
    }


    async function loadRecommendations() {
      try {
        setLoading(true);
        setError("");
        setRecommendations([]);

        const data = await getRecommendations(
          track.track_id
        );

        setRecommendations(data.results || []);

      } catch (error) {
        console.error(
          "Recommendation error:",
          error
        );

        setError(
          "Could not load similar songs."
        );

      } finally {
        setLoading(false);
      }
    }


    loadRecommendations();

  }, [track]);


  function handleSelectSimilarTrack(selectedTrack) {
    navigate(`/song/${selectedTrack.track_id}`, {
      state: {
        track: selectedTrack,
      },
    });
  }


  if (!track) {
    return (
      <main className="simple-page">

        <section className="empty-state">

          <div className="empty-icon">
            🎵
          </div>


          <h2>
            Song not found
          </h2>


          <p>
            Please select a song from Discover.
          </p>


          <button
            type="button"
            className="back-button"
            onClick={() => navigate("/")}
          >
            ← Back to Discover
          </button>

        </section>

      </main>
    );
  }


  const artists = Array.isArray(track.artists)
    ? track.artists.join(", ")
    : track.artists;


  return (
    <main className="song-page">

      <section className="song-hero">

        <button
          type="button"
          className="song-back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>


        <div className="song-details">

          <div className="song-art">
            🎵
          </div>


          <div className="song-info">

            <span className="page-label">
              NOW EXPLORING
            </span>


            <h1>
              {track.track_name}
            </h1>


            <p className="song-artist">
              {artists}
            </p>


            {track.album_name && (
              <p className="song-album">
                {track.album_name}
              </p>
            )}


            <div className="song-meta">

              {track.genres?.length > 0 && (

                <div className="song-genres">

                  {track.genres.map((genre) => (

                    <span
                      className="genre-badge"
                      key={genre}
                    >
                      {genre}
                    </span>

                  ))}

                </div>

              )}


              {track.track_genre &&
                !track.genres?.length && (

                  <div className="song-genres">

                    <span className="genre-badge">
                      {track.track_genre}
                    </span>

                  </div>

                )}


              {track.popularity !== undefined &&
                track.popularity !== null && (

                  <div className="song-popularity">

                    <span className="popularity-dot"></span>

                    Popularity {track.popularity}

                  </div>

                )}

            </div>

          </div>

        </div>

      </section>


      <section className="content-section recommendations-section">

        <div className="recommendation-header">

          <div>

            <span className="section-label">
              AI RECOMMENDATIONS
            </span>


            <h2>
              Similar songs you might like
            </h2>


            <p>
              Music selected based on similarity to
              <strong> {track.track_name}</strong>.
            </p>

          </div>


          <div className="ai-badge">
            ✦ AI Powered
          </div>

        </div>


        <div className="recommendation-intro">

          <span>✨</span>

          <p>
            These recommendations are based on the
            musical characteristics of this track.
          </p>

        </div>


        {error && (

          <div className="message error-message">

            <span>!</span>

            {error}

          </div>

        )}


        {loading && (

          <div className="recommendation-loading">

            <div className="loading-spinner"></div>

            <div>

              <strong>
                Finding similar songs...
              </strong>

              <p>
                Our AI is analyzing the music.
              </p>

            </div>

          </div>

        )}


        {!loading &&
          recommendations.length > 0 && (

            <div className="track-grid">

              {recommendations.map(
                (recommendedTrack) => (

                  <TrackCard
                    key={recommendedTrack.track_id}
                    track={recommendedTrack}
                    onSelect={
                      handleSelectSimilarTrack
                    }
                  />

                )
              )}

            </div>

          )}


        {!loading &&
          !error &&
          recommendations.length === 0 && (

            <div className="empty-state small">

              <div className="empty-icon">
                🎧
              </div>

              <h2>
                No similar songs found
              </h2>

              <p>
                Try exploring another song.
              </p>

            </div>

          )}

      </section>

    </main>
  );
}


export default Song;