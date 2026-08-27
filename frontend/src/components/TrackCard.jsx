import { useNavigate } from "react-router-dom";

function TrackCard({ track, onSelect }) {
  const navigate = useNavigate();

  function handleCardClick() {
    if (onSelect) {
      onSelect(track);
      return;
    }

    navigate(`/song/${track.track_id}`, {
      state: {
        track,
      },
    });
  }

  const artists = Array.isArray(track.artists)
    ? track.artists.join(", ")
    : track.artists;

  return (
    <button
      type="button"
      className="track-card"
      onClick={handleCardClick}
    >

      <div className="track-art">
        <span>🎵</span>
      </div>


      <div className="track-info">

        <h3 title={track.track_name}>
          {track.track_name}
        </h3>


        <p title={artists}>
          {artists}
        </p>


        <div className="track-meta">

          {track.track_genre && (
            <span className="genre-badge">
              {track.track_genre}
            </span>
          )}


          {track.genres?.length > 0 &&
            !track.track_genre && (
              <span className="genre-badge">
                {track.genres[0]}
              </span>
            )}


          {track.popularity !== undefined &&
            track.popularity !== null && (

              <span className="popularity">

                <span className="popularity-dot"></span>

                {track.popularity}

              </span>

            )}

        </div>

      </div>


      <div className="track-arrow">
        →
      </div>

    </button>
  );
}

export default TrackCard;