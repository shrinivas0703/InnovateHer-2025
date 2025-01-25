"use client"; // Ensures the component is client-side only

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { LatLngTuple } from "leaflet";

// Dynamically import MapContainer and related components from react-leaflet
// Dynamically import MapContainer and related components from react-leaflet
const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(mod => mod.Popup), { ssr: false });

import "leaflet/dist/leaflet.css";


const USMap: React.FC = () => {
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setMapLoaded(true); // Only set map loaded after the client side is available
    }
  }, []);

  if (!mapLoaded) {
    return <div>Loading map...</div>;
  }
  const maxZoom = 10;
  const minZoom = 4;

  // Define the bounds of the map (the US)
  const bounds: [LatLngTuple, LatLngTuple] = [
    [18.7763, -179.1486], // Southwest corner (including Alaska & Hawaii)
    [71.5388001, -66.93457], // Northeast corner (continental US including Alaska)
  ];

  return (
    <div style={{ height: "500px", width: "100%" }}>
      {mapLoaded && (
        <MapContainer
          center={[37.0902, -95.7129]} // Center of the US (approx.)
          zoom={4}
          maxZoom={maxZoom}
          minZoom={minZoom}
          bounds={bounds}
          style={{ height: "100%", width: "100%" }}
          maxBounds={bounds}
        >
          {/* TileLayer for rendering the map */}
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
          />
        </MapContainer>
      )}
      {!mapLoaded && <div>Loading map...</div>}
    </div>
  );
};

export default USMap;
