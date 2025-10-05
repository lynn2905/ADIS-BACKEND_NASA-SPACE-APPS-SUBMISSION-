import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const ESRI_URL =
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const CARTO_LABELS_URL =
  "https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png";

export default function LeafletView({ city, onBack }) {
  const mapDiv = useRef(null);

  useEffect(() => {
    if (!mapDiv.current) return;
    const map = L.map(mapDiv.current, { zoomControl: true, worldCopyJump: true })
      .setView([20, 0], 2);

    L.tileLayer(ESRI_URL, { maxZoom: 19, minZoom: 2 }).addTo(map);
    L.tileLayer(CARTO_LABELS_URL, { maxZoom: 19, minZoom: 2 }).addTo(map);

    if (city?.lat && city?.lon) {
      map.flyTo([city.lat, city.lon], 7, { duration: 1.5 });
      L.marker([city.lat, city.lon]).addTo(map);
    }
    return () => map.remove();
  }, [city]);

  // Optional: hotkey 'g' to go back without a button
  useEffect(() => {
    if (!onBack) return;
    const h = (e) => { if (e.key.toLowerCase() === "g") onBack(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onBack]);

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, background: "#0b1020" }}>
      <div ref={mapDiv} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
