import { Link } from "react-router-dom";

function Theme({ theme, setTheme }) {
  const themes = [
    {
      id: "dark",
      icon: "🌙",
      title: "Dark",
      description: "Dark and easy on the eyes.",
    },
    {
      id: "light",
      icon: "☀️",
      title: "Light",
      description: "Clean and bright.",
    },
    {
      id: "indigo",
      icon: "●",
      title: "Default",
      description: "The original classic look of Music Mind.",
    },
  ];

  return (
    <main className="theme-page">
      <section className="theme-section">

        <div className="page-label">
          Appearance
        </div>

        <h1>Choose Your Theme</h1>

        <p className="theme-description">
          Customize the look and feel of Music Mind.
        </p>

        <div className="theme-options">

          {themes.map((item) => (
            <button
              key={item.id}
              className={`theme-option ${
                theme === item.id ? "selected" : ""
              }`}
              onClick={() => setTheme(item.id)}
              aria-pressed={theme === item.id}
            >
              <span
                className={`theme-icon ${
                  item.id === "indigo" ? "default-dot" : ""
                }`}
              >
                {item.icon}
              </span>

              <div className="theme-option-content">
                <h2>{item.title}</h2>

                <p>{item.description}</p>
              </div>

              <span className="theme-check">
                {theme === item.id ? "✓" : ""}
              </span>
            </button>
          ))}

        </div>

        {/* BACK BUTTON */}

        <Link to="/" className="theme-back-button">
          <span>←</span>
          Back to Discover
        </Link>

      </section>
    </main>
  );
}

export default Theme;