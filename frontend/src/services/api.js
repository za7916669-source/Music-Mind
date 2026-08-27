const API_BASE_URL =
  "https://humble-enthusiasm-production-160b.up.railway.app";

export async function searchTracks(query) {
  const response = await fetch(
    `${API_BASE_URL}/tracks/search?q=${encodeURIComponent(query)}`
  );

  if (!response.ok) {
    throw new Error("Failed to search tracks");
  }

  return response.json();
}

export async function getRecommendations(trackId, limit = 10) {
  const response = await fetch(
    `${API_BASE_URL}/recommendations/${trackId}?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to get recommendations");
  }

  return response.json();
}