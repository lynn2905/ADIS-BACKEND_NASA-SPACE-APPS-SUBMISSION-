import { X } from "lucide-react";
import { aqiColor, getAQICategory } from "../utils/aqi";

export default function CityCard({ city, onClose }) {
  if (!city) return null;
  return (
    <div className="absolute top-4 right-4 max-w-sm bg-slate-900/80 backdrop-blur border border-slate-700 rounded-xl shadow-md p-4 text-white">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{city.name}</h3>
          <p className="text-sm text-gray-300">{city.lat.toFixed(2)}°, {city.lon.toFixed(2)}°</p>
        </div>
        <button onClick={onClose} className="text-gray-300 hover:text-white" aria-label="Close city details">
          <X size={18} />
        </button>
      </div>
      <div className="mt-3 flex items-center gap-3">
        <span className="inline-block w-3 h-3 rounded" style={{ background: aqiColor(city.aqi) }} />
        <div>
          <div className="text-sm">AQI: <span className="font-semibold">{city.aqi}</span></div>
          <div className="text-sm text-gray-300">{getAQICategory(city.aqi).level}</div>
        </div>
      </div>
      <p className="mt-2 text-xs text-gray-300">{getAQICategory(city.aqi).desc}</p>
    </div>
  );
}
