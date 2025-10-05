import { Info } from "lucide-react";
import { AQI_LEGEND } from "../utils/aqi";

export default function Legend() {
  return (
    <div className="absolute bottom-4 left-4 bg-slate-900/70 backdrop-blur rounded-lg p-3 text-xs text-white">
      <div className="font-semibold mb-2 flex items-center gap-2"><Info size={14} /> AQI legend</div>
      <div className="grid grid-cols-3 gap-2">
        {AQI_LEGEND.map((l) => (
          <div key={l.label} className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded" style={{ background: l.color }} />
            <span>{l.label} <span className="text-gray-400">{l.range}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}
