import Header from "./components/Header";
import { useState } from "react";
import { searchTracks } from "./services/api";

function App() {
 const [searchQuery, setSearchQuery] = useState("");

 const[results, setResults] = useState([]);

 async function handleSearch(){
  if(!searchQuery.trim()){
    return;
  }

  try{
    const data = await searchTracks(searchQuery);
     
    setResults(data.results);
  } catch(error) {
    console.error(error);
  }
 }

  return (
    <div>
       <Header />


 <input
  type="text"
  placeholder="Search for a song or artist..."
  value={searchQuery}
  onChange={(event) => setSearchQuery(event.target.value)}
/>
      <button onClick={handleSearch}>
       search
      </button>

      <div>
        {results.map((track) =>( 
          <div key={track.track_id}>
            <h3>{track.track_name}</h3>
            <p>{track.artists.join(", ")}</p>
            <p>{track.album_name}</p>
      </div>
        ))}
        </div> 

      <p>You searched for: {searchQuery}</p>
    </div>
  );
}

export default App;