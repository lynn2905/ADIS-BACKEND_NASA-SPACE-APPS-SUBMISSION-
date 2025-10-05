import { useEffect, useRef } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { getGmapsKey, getMapId } from "../utils/keys";

export default function GoogleMapView({ city, onError }) {
  const divRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const key = getGmapsKey();
        const mapId = getMapId();
        if (!key) throw new Error("Google Maps key missing");
        await new Loader({ apiKey: key, version: "weekly" }).load();
        if (cancelled) return;
        const map = new google.maps.Map(divRef.current, {
          center: { lat: 20, lng: 0 }, zoom: 3, tilt: 67.5, heading: 0, mapId: mapId || undefined, disableDefaultUI: true,
        });
        mapRef.current = map;
        if (city) {
          if (map.moveCamera) map.moveCamera({ center: { lat: city.lat, lng: city.lon }, zoom: 11, tilt: 67.5, heading: 0 });
          else { map.setCenter({ lat: city.lat, lng: city.lon }); map.setZoom(11); }
          new google.maps.Marker({ position: { lat: city.lat, lng: city.lon }, map });
        }
      } catch (e) { onError?.(e?.message || String(e)); }
    })();
    return () => { cancelled = true; };
  }, [city]);

  return <div ref={divRef} className="absolute inset-0" />;
}
