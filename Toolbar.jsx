import { RotateCw } from "lucide-react";
export default function Toolbar({ view, onReload, onBack }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-2 text-gray-300 text-sm">
        <RotateCw size={16} />
        <span>
          {view === "globe" && "Drag to explore. Click a marker."}
          {view === "map" && "Google Maps view"}
          {view === "leaflet" && "Leaflet view"}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={onReload} className="px-2 py-1 rounded-md text-xs bg-slate-700 hover:bg-slate-600 text-white">Reload data</button>
        {view !== 'globe' && (
          <button onClick={onBack} className="px-2 py-1 rounded-md text-xs bg-slate-700 hover:bg-slate-600 text-white">Back to globe</button>
        )}
      </div>
    </div>
  );
}
