import { NavLink } from "react-router-dom";

function Header() {
  return (
    <header className="header">

      <div className="header-content">

        <NavLink to="/" className="logo">
          <span className="logo-icon">🎵</span>

          <span className="logo-text">
            Music Mind
          </span>
        </NavLink>


        <nav className="main-nav">

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            Discover
          </NavLink>


          <NavLink
            to="/explore"
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            Explore
          </NavLink>


          <NavLink
            to="/about"
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            About
          </NavLink>


          <NavLink
            to="/theme"
            className={({ isActive }) =>
              `theme-button ${isActive ? "active" : ""}`
            }
            title="Theme Settings"
            aria-label="Theme Settings"
          >
            ⚙️
          </NavLink>

        </nav>

      </div>


      <div className="eyebrow-wrap">

        <span className="eyebrow-badge">

          <span className="eyebrow-dot"></span>

          Discover music you'll love

        </span>

      </div>

    </header>
  );
}

export default Header;