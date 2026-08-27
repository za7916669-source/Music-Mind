import { Routes, Route } from "react-router-dom";
import { useState } from "react";

import Header from "./components/Header";
import Theme from "./components/Theme";

import Discover from "./pages/Discover";
import Explore from "./pages/Explore";
import About from "./pages/About";
import Song from "./pages/Song";

import "./App.css";

function App() {
  const [theme, setTheme] = useState("indigo");

  return (
    <div className="app" data-theme={theme}>
      <Header />

      <Routes>
        <Route path="/" element={<Discover />} />

        <Route path="/explore" element={<Explore />} />

        <Route path="/about" element={<About />} />

        <Route
          path="/theme"
          element={
            <Theme
              theme={theme}
              setTheme={setTheme}
            />
          }
        />

        <Route path="/song/:id" element={<Song />} />
      </Routes>
    </div>
  );
}

export default App;