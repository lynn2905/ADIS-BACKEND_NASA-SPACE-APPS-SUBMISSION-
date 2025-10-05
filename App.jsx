import { useEffect, useRef, useState, useCallback } from "react";
import { Wind, AlertTriangle } from "lucide-react";
import Globe from "./components/Globe";
import GoogleMapView from "./components/GoogleMapView";
import LeafletView from "./components/LeafletView";
import Legend from "./components/Legend";
import Toolbar from "./components/Toolbar";
import CityCard from "./components/CityCard";
import { hydrateCredsFromQueryAndMeta } from "./utils/keys";

// Expanded city list (50+)
const CITIES = [
  // Asia - High pollution hotspots
  { name: "Delhi", lat: 28.6, lon: 77.2, aqi: 387 },
  { name: "Beijing", lat: 39.9, lon: 116.4, aqi: 178 },
  { name: "Dhaka", lat: 23.8, lon: 90.4, aqi: 296 },
  { name: "Mumbai", lat: 19.1, lon: 72.9, aqi: 164 },
  { name: "Lahore", lat: 31.5, lon: 74.3, aqi: 312 },
  { name: "Jakarta", lat: -6.2, lon: 106.8, aqi: 156 },
  { name: "Kolkata", lat: 22.6, lon: 88.4, aqi: 245 },
  { name: "Shanghai", lat: 31.2, lon: 121.5, aqi: 142 },
  { name: "Seoul", lat: 37.6, lon: 127.0, aqi: 98 },
  { name: "Tokyo", lat: 35.7, lon: 139.7, aqi: 67 },
  { name: "Bangkok", lat: 13.8, lon: 100.5, aqi: 134 },
  { name: "Hanoi", lat: 21.0, lon: 105.8, aqi: 167 },
  { name: "Karachi", lat: 24.9, lon: 67.0, aqi: 203 },
  { name: "Tehran", lat: 35.7, lon: 51.4, aqi: 198 },
  { name: "Ulaanbaatar", lat: 47.9, lon: 106.9, aqi: 289 },
  { name: "Kathmandu", lat: 27.7, lon: 85.3, aqi: 214 },
  { name: "Chengdu", lat: 30.7, lon: 104.1, aqi: 156 },
  { name: "Ho Chi Minh City", lat: 10.8, lon: 106.7, aqi: 123 },

  // Middle East & Africa
  { name: "Cairo", lat: 30.0, lon: 31.2, aqi: 168 },
  { name: "Dubai", lat: 25.3, lon: 55.3, aqi: 112 },
  { name: "Riyadh", lat: 24.7, lon: 46.7, aqi: 134 },
  { name: "Baghdad", lat: 33.3, lon: 44.4, aqi: 189 },
  { name: "Lagos", lat: 6.5, lon: 3.4, aqi: 145 },
  { name: "Nairobi", lat: -1.3, lon: 36.8, aqi: 87 },
  { name: "Johannesburg", lat: -26.2, lon: 28.0, aqi: 76 },
  { name: "Addis Ababa", lat: 9.0, lon: 38.7, aqi: 94 },

  // Europe
  { name: "London", lat: 51.5, lon: -0.1, aqi: 52 },
  { name: "Paris", lat: 48.9, lon: 2.4, aqi: 61 },
  { name: "Moscow", lat: 55.8, lon: 37.6, aqi: 64 },
  { name: "Istanbul", lat: 41.0, lon: 28.9, aqi: 89 },
  { name: "Berlin", lat: 52.5, lon: 13.4, aqi: 48 },
  { name: "Rome", lat: 41.9, lon: 12.5, aqi: 73 },
  { name: "Madrid", lat: 40.4, lon: -3.7, aqi: 58 },
  { name: "Warsaw", lat: 52.2, lon: 21.0, aqi: 82 },
  { name: "Athens", lat: 38.0, lon: 23.7, aqi: 91 },

  // North America
  { name: "Los Angeles", lat: 34.1, lon: -118.2, aqi: 87 },
  { name: "Mexico City", lat: 19.4, lon: -99.1, aqi: 124 },
  { name: "New York", lat: 40.7, lon: -74.0, aqi: 54 },
  { name: "Chicago", lat: 41.9, lon: -87.6, aqi: 62 },
  { name: "Houston", lat: 29.8, lon: -95.4, aqi: 71 },
  { name: "Phoenix", lat: 33.4, lon: -112.1, aqi: 79 },
  { name: "Toronto", lat: 43.7, lon: -79.4, aqi: 45 },
  { name: "Vancouver", lat: 49.3, lon: -123.1, aqi: 38 },
  { name: "Montreal", lat: 45.5, lon: -73.6, aqi: 41 },

  // South America
  { name: "São Paulo", lat: -23.5, lon: -46.6, aqi: 78 },
  { name: "Rio de Janeiro", lat: -22.9, lon: -43.2, aqi: 67 },
  { name: "Buenos Aires", lat: -34.6, lon: -58.4, aqi: 73 },
  { name: "Lima", lat: -12.0, lon: -77.0, aqi: 98 },
  { name: "Bogotá", lat: 4.7, lon: -74.1, aqi: 102 },
  { name: "Santiago", lat: -33.4, lon: -70.7, aqi: 112 },

  // Oceania
  { name: "Sydney", lat: -33.9, lon: 151.2, aqi: 34 },
  { name: "Melbourne", lat: -37.8, lon: 144.9, aqi: 39 },
  { name: "Auckland", lat: -36.8, lon: 174.8, aqi: 28 },
  { name: "Perth", lat: -31.9, lon: 115.9, aqi: 31 },
];

export default function App() {
  const globeRef = useRef(null);
  const [view, setView] = useState("globe"); // globe | map | leaflet
  const [mapsError, setMapsError] = useState(null);
  const [leafError, setLeafError] = useState(null);
  const [selectedCity, setSelectedCity] = useState(null);
  const [cities] = useState(CITIES);

  useEffect(() => {
    hydrateCredsFromQueryAndMeta();
  }, []);

  const hasGmapsKey = () =>
    !!(window.__GMAPS_KEY__ || localStorage.getItem("gmaps.key") || import.meta.env?.VITE_GMAPS_KEY);

  const handleBack = useCallback(() => {
    setSelectedCity(null);
    setView("globe");
    setTimeout(() => window.dispatchEvent(new Event("resize")), 0);
  }, []);

  function handleMarkerClick(city) {
    setSelectedCity(city);               // ask first (don’t switch yet)
    globeRef.current?.flyToCity?.(city); // animate globe
  }

  function onGoogleError(msg) {
    setMapsError(msg || "Google Maps failed. Falling back.");
    setView("leaflet");
  }

  return (
    <>
      {view === "globe" && (
        <div className="w-full min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 p-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-6">
              <div className="flex items-center justify-center gap-3 mb-2">
                <Wind className="text-red-400" size={32} />
                <h1 className="text-4xl font-bold text-white">ADIS — Atmospheric Digital Immune System</h1>
              </div>
              <p className="text-gray-300">Click a city dot. Choose whether to open a map.</p>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 shadow-xl relative mb-4">
              <Toolbar view={view} onReload={() => { /* no-op here */ }} onBack={handleBack} />

              <Globe ref={globeRef} cities={cities} onMarkerClick={handleMarkerClick} />

              <Legend />

              {selectedCity && (
                <CityCard city={selectedCity} onClose={() => setSelectedCity(null)} />
              )}

              {/* Confirmation bar */}
              {selectedCity && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[10000] bg-slate-900/95 border border-slate-700 text-white rounded-lg shadow px-4 py-3 flex items-center gap-3">
                  <div className="text-sm">
                    <div className="font-semibold">{selectedCity.name}</div>
                    <div className="text-xs opacity-80">
                      Lat {selectedCity.lat}, Lon {selectedCity.lon}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-2">
                    <button
                      onClick={() => setView(hasGmapsKey() ? "map" : "leaflet")}
                      className="px-3 py-1.5 text-sm rounded bg-blue-600 hover:bg-blue-500"
                    >
                      Open map
                    </button>
                    {hasGmapsKey() && (
                      <button
                        onClick={() => setView("map")}
                        className="px-3 py-1.5 text-sm rounded bg-sky-700 hover:bg-sky-600"
                      >
                        Google Maps
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {view !== "globe" && (
        <button
          onClick={handleBack}
          className="fixed top-4 right-4 z-[11000] px-3 py-2 rounded bg-slate-700 text-white hover:bg-slate-600 shadow"
        >
          Back to globe
        </button>
      )}

      {view === "map" && (
        <GoogleMapView city={selectedCity} onError={onGoogleError} onBack={handleBack} />
      )}

      {view === "leaflet" && (
        <LeafletView city={selectedCity} onBack={handleBack} />
      )}

      {mapsError && view === "map" && (
        <div className="fixed top-4 left-4 right-4 max-w-xl bg-red-900/80 text-red-100 border border-red-500 rounded-lg px-3 py-2 z-[10000]">
          <div className="flex gap-2 items-start text-xs">
            <AlertTriangle size={16} className="mt-0.5" />
            <div>
              <div className="font-semibold">Google Maps error</div>
              <div className="mb-1">{mapsError}</div>
              <div className="opacity-80">
                Provide a key via window.__GMAPS_KEY__, localStorage('gmaps.key'), URL ?gmaps_key=..., meta name=gmaps-key, or env (VITE_GMAPS_KEY).
              </div>
            </div>
          </div>
        </div>
      )}

      {leafError && view === "leaflet" && (
        <div className="fixed top-4 left-4 bg-yellow-900/80 text-yellow-100 border border-yellow-500 rounded-lg px-3 py-2 text-xs z-[10000]">
          {leafError}
        </div>
      )}
    </>
  );
}
