function About() {
  return (
    <main className="about-page">

      <section className="about-hero">

  <div className="about-hero-content">

    <h1>
      Music discovery,
      <br />
      <span>made personal.</span>
    </h1>

    <p>
      Music Mind is an AI-powered music discovery
      system designed to help you find songs that
      match the music you already love.
    </p>

  </div>

</section>

<div className="about-content">

  <div className="about-section-heading">

    <div>

      <div className="about-label">
        <span className="about-label-dot"></span>
        ABOUT MUSIC MIND
      </div>

      <h2>
        How MusicMind works
      </h2>

    </div>

    <span className="about-section-description">
      From finding a track to discovering your next favorite sound.
    </span>

  </div>


  <div className="about-grid">

    {/* your existing three about cards here */}

  </div>

</div>


      <section className="about-grid">

        <article className="about-card">

          <span className="about-number">
            01
          </span>

          <h2>
            Search
          </h2>

          <p>
            Search for a song or artist and find tracks
            from the Music Mind database.
          </p>

        </article>


        <article className="about-card">

          <span className="about-number">
            02
          </span>

          <h2>
            Discover
          </h2>

          <p>
            Select a track that you like and let Music Mind
            analyze its characteristics.
          </p>

        </article>


        <article className="about-card">

          <span className="about-number">
            03
          </span>

          <h2>
            Recommend
          </h2>

          <p>
            Our recommendation system finds songs with
            similar musical characteristics.
          </p>

        </article>

      </section>


      <section className="technology-section">

        <span className="page-eyebrow">
          BUILT WITH
        </span>


        <div className="technology-list">

          <span>React</span>
          <span>FastAPI</span>
          <span>Python</span>
          <span>Machine Learning</span>
          <span>SQLite</span>

        </div>

      </section>

    </main>
  );
}

export default About;
