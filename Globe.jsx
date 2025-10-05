import { useEffect, useRef, useState, forwardRef, useImperativeHandle } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { aqiColor } from "../utils/aqi";
import { latLonToVector3, RADIUS } from "../utils/geo";

export default forwardRef(function Globe({ cities, onMarkerClick }, ref) {
  const mountRef = useRef(null);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const globeRef = useRef(null);
  const markersGroupRef = useRef(null);
  const hazesGroupRef = useRef(null);
  const pollutionGroupRef = useRef(null);
  const markerMeshesRef = useRef([]);
  const texturesRef = useRef([]);
  const [pollutionData, setPollutionData] = useState([]);

  // Load pollution data from fused_data.json
  useEffect(() => {
    fetch('/fused_data.json')
      .then(res => res.json())
      .then(data => {
        console.log(`Loaded ${data.length} pollution data points`);
        // Filter out invalid NO2 values
        const validData = data.filter(d => d.NO2 > -1e20);
        console.log(`Valid data points: ${validData.length}`);
        setPollutionData(validData);
      })
      .catch(err => {
        console.error('Error loading pollution data:', err);
      });
  }, []);

  useImperativeHandle(ref, () => ({
    resetView() {
      const camera = cameraRef.current; const controls = controlsRef.current; if (!camera || !controls) return;
      camera.position.set(0, 0, 320); controls.target.set(0, 0, 0); controls.autoRotate = true; controls.update();
    },
    flyToCity(city, onDone) {
      const controls = controlsRef.current; const camera = cameraRef.current; if (!controls || !camera) return;
      controls.autoRotate = false;
      const target = latLonToVector3(city.lat, city.lon, RADIUS);
      const startPos = camera.position.clone(); const endPos = target.clone().normalize().multiplyScalar(260);
      const startTgt = controls.target.clone(); const endTgt = target.clone().multiplyScalar(0.98);
      const t0 = performance.now(); const DUR = 900;
      const step = (now) => { const t = Math.min(1, (now - t0) / DUR); camera.position.lerpVectors(startPos, endPos, t); controls.target.lerpVectors(startTgt, endTgt, t); controls.update(); if (t < 1) requestAnimationFrame(step); else onDone?.(); };
      requestAnimationFrame(step);
    }
  }), []);

  useEffect(() => {
    const mount = mountRef.current; if (!mount) return;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight); mount.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0a0e1a); sceneRef.current = scene;
    const camera = new THREE.PerspectiveCamera(45, mount.clientWidth / mount.clientHeight, 0.1, 2000); camera.position.set(0, 0, 320); cameraRef.current = camera;
    scene.add(new THREE.AmbientLight(0xffffff, 0.45)); const key = new THREE.PointLight(0xffffff, 1.0); key.position.set(250, 200, 200); scene.add(key);

    const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.enablePan = false; controls.minDistance = RADIUS + 40; controls.maxDistance = RADIUS + 350; controls.autoRotate = true; controls.autoRotateSpeed = 0.35; controlsRef.current = controls;

    const loader = new THREE.TextureLoader();
    const urls = [
      "https://threejs.org/examples/textures/land_ocean_ice_cloud_2048.jpg",
      "https://threejs.org/examples/textures/earthbump1k.jpg",
      "https://threejs.org/examples/textures/earthspec1k.jpg",
    ];
    const [mapTex, bumpTex, specTex] = urls.map((u) => loader.load(u, (t) => texturesRef.current.push(t)));
    const globeMat = new THREE.MeshPhongMaterial({ map: mapTex, bumpMap: bumpTex, bumpScale: 0.5, specularMap: specTex, specular: new THREE.Color("grey") });
    const globe = new THREE.Mesh(new THREE.SphereGeometry(RADIUS, 64, 64), globeMat); scene.add(globe); globeRef.current = globe;

    const hazes = new THREE.Group(); const markers = new THREE.Group(); const pollution = new THREE.Group();
    globe.add(hazes); globe.add(markers); globe.add(pollution);
    hazesGroupRef.current = hazes; markersGroupRef.current = markers; pollutionGroupRef.current = pollution;

    const raycaster = new THREE.Raycaster(); const pointer = new THREE.Vector2();
   const onClick = (event) => {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);

  // Check if user clicked a city marker first
  const hits = raycaster.intersectObjects(markerMeshesRef.current, false);
  if (hits.length > 0) {
    const city = hits[0].object.userData.city;
    onMarkerClick?.(city);
    return;
  }

  // 🟢 Otherwise, check if clicked the globe surface
  const globeHit = raycaster.intersectObject(globeRef.current, false);
  if (globeHit.length > 0) {
    const point = globeHit[0].point;
    // Convert 3D point to lat/lon
    const lat = 90 - (Math.acos(point.y / RADIUS) * 180) / Math.PI;
    const lon = ((Math.atan2(point.z, point.x) * 180) / Math.PI) - 180;

    // Call the same function, but with a "virtual city"
    onMarkerClick?.({ lat, lon, name: "Selected Location" });
  }
};
    renderer.domElement.addEventListener("click", onClick);

    const ro = new ResizeObserver(() => { const w = mount.clientWidth; const h = mount.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }); ro.observe(mount);
    renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

    return () => {
      ro.disconnect(); renderer.setAnimationLoop(null); renderer.domElement.removeEventListener("click", onClick); controls.dispose();
      const disposeNode = (o) => { if (o.geometry) o.geometry.dispose(); if (o.material) { Array.isArray(o.material) ? o.material.forEach((m)=>m.dispose()) : o.material.dispose(); } };
      scene.traverse(disposeNode); texturesRef.current.forEach((t) => t?.dispose()); renderer.dispose(); mount.removeChild(renderer.domElement);
    };
  }, []);

  // Add pollution data points
  useEffect(() => {
    const globe = globeRef.current;
    const pollution = pollutionGroupRef.current;
    if (!globe || !pollution || pollutionData.length === 0) return;

    // Clear existing pollution points
    for (let i = pollution.children.length - 1; i >= 0; i--) {
      const c = pollution.children[i];
      c.geometry?.dispose();
      if (c.material) c.material.dispose();
      pollution.remove(c);
    }

    console.log(`Rendering ${pollutionData.length} pollution points`);

    // Helper to calculate AQI from NO2
    function calculateAQI(NO2) {
      if (NO2 < 0 || NO2 === -1e30) return 0;
      // Scale NO2 to AQI (simplified)
      const aqi = Math.min(500, Math.max(0, NO2 * 1e15 * 50));
      return aqi;
    }

    // Create point geometry
    const pointGeom = new THREE.SphereGeometry(0.8, 8, 8);

    // Sample data if too large (for performance)
    const maxPoints = 20000;
    const dataToRender = pollutionData.length > maxPoints 
      ? pollutionData.filter((_, i) => i % Math.ceil(pollutionData.length / maxPoints) === 0)
      : pollutionData;

    console.log(`Rendering ${dataToRender.length} points (sampled from ${pollutionData.length})`);

    dataToRender.forEach((point) => {
      const aqi = calculateAQI(point.NO2);
      const color = aqiColor(aqi);
      const pos = latLonToVector3(point.lat, point.lon, RADIUS + 0.5);

      const mesh = new THREE.Mesh(
        pointGeom,
        new THREE.MeshBasicMaterial({
          color,
          transparent: true,
          opacity: 0.7
        })
      );
      mesh.position.copy(pos);
      pollution.add(mesh);

      // Add glow for anomalies
      if (point.anomaly_flag === 1) {
        const glowMesh = new THREE.Mesh(
          new THREE.SphereGeometry(1.5, 8, 8),
          new THREE.MeshBasicMaterial({
            color: 0xff0000,
            transparent: true,
            opacity: 0.4,
            blending: THREE.AdditiveBlending
          })
        );
        glowMesh.position.copy(pos);
        pollution.add(glowMesh);
      }
    });

    console.log(`Added ${pollution.children.length} meshes to scene`);
  }, [pollutionData]);

  // City markers (rendered on top of pollution data)
  useEffect(() => {
    const globe = globeRef.current; const markers = markersGroupRef.current; const hazes = hazesGroupRef.current;
    if (!globe || !markers || !hazes) return;
    for (const g of [markers, hazes]) {
      for (let i = g.children.length - 1; i >= 0; i--) {
        const c = g.children[i]; c.geometry?.dispose();
        if (c.material) (Array.isArray(c.material) ? c.material.forEach((m)=>m.dispose()) : c.material.dispose());
        g.remove(c);
      }
    }
    markerMeshesRef.current = [];

    const markerGeom = new THREE.SphereGeometry(2.2, 16, 16);
    cities.forEach((c) => {
      const color = aqiColor(c.aqi); const pos = latLonToVector3(c.lat, c.lon);
      const marker = new THREE.Mesh(markerGeom, new THREE.MeshBasicMaterial({ color }));
      marker.position.copy(pos); marker.lookAt(new THREE.Vector3(0,0,0)); marker.userData.city = c;
      markers.add(marker); markerMeshesRef.current.push(marker);
      if (c.aqi > 150) {
        const hazeSize = Math.min(18, c.aqi / 18);
        const haze = new THREE.Mesh(new THREE.SphereGeometry(hazeSize, 20, 20), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.28, depthWrite: false, blending: THREE.AdditiveBlending }));
        haze.position.copy(pos); hazes.add(haze);
      }
    });
  }, [cities]);

  return <div ref={mountRef} className="w-full bg-slate-900 rounded-lg overflow-hidden" style={{ height: "600px" }} />;
});