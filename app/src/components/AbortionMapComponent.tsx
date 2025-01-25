"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { LatLngTuple } from "leaflet";
import { GeoJSON, useMap } from "react-leaflet";
import L from "leaflet"; // Import Leaflet explicitly

const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });

import "leaflet/dist/leaflet.css";

// Type for the state info mapping (state name -> number)
type StateInfo = { [key: string]: number };

// Type for the color description map (color -> description)
type ColorDesc = { [key: string]: string };

const USAbortionMap: React.FC = () => {
    const [mapLoaded, setMapLoaded] = useState<boolean>(false);
    const [stateInfo, setStateInfo] = useState<StateInfo>({});
    const [numFeatureMap, setNumFeatureMap] = useState<{ [key: number]: string }>({});
    const [geojsonData, setGeojsonData] = useState<any>(null);

    useEffect(() => {
        if (typeof window !== "undefined") {
            setMapLoaded(true);
        }

        const fetchData = async () => {
            try {
                const response = await fetch("http://localhost:8000/abortion_info");
                if (!response.ok) {
                    throw new Error(`Error fetching data: ${response.statusText}`);
                }
                const data = await response.json();
                const geoJsonResponse = await fetch("/data/us-states.json");
                const geoJsonData = await geoJsonResponse.json();
                setGeojsonData(geoJsonData);
                setStateInfo(data.state_info);
                setNumFeatureMap(data.num_feature_map);
            } catch (error) {
                console.error("Error fetching Medicaid info:", error);
            }
        };

        fetchData();
    }, []);

    if (!mapLoaded) {
        return <div>Loading map...</div>;
    }

    const colorMap: { [key: number]: string } = {
        0: "#ff0000", // Red
        1: "#ff7f00", // Orange
        2: "#ffff00", // Yellow
        3: "#7fff00", // Light Green
        4: "#00ff00", // Green
    };

    const colorDesc: ColorDesc = {
        "#ff0000": numFeatureMap[0],
        "#ff7f00": numFeatureMap[1],
        "#ffff00": numFeatureMap[2],
        "#7fff00": numFeatureMap[3],
        "#00ff00": numFeatureMap[4],
    };

    const getStateColor = (state: string) => {
        const stateNumber = stateInfo[state];
        return stateNumber !== undefined && colorMap[stateNumber]
            ? colorMap[stateNumber]
            : "#cccccc"; // Default color for missing values
    };

    // Legend component as a Leaflet control
    const Legend = () => {
        const map = useMap();

        useEffect(() => {
            const legend = new L.Control({ position: "bottomleft" });

            legend.onAdd = () => {
                const div = L.DomUtil.create("div", "info legend");
                div.style.backgroundColor = "rgba(255, 255, 255, 0.8)"; // Semi-transparent background
                div.style.padding = "8px"; // Smaller padding
                div.style.borderRadius = "8px"; // Slightly larger rounded corners
                div.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)"; // Softer shadow
                div.style.fontFamily = "Arial, sans-serif"; // Modern font
                div.style.fontSize = "12px"; // Smaller font size

                div.innerHTML = `
                    <h4 style="margin: 0 0 6px; font-size: 14px; font-weight: bold; text-align: center; color: #333;">Legend</h4>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                `;
                for (const [color, description] of Object.entries(colorDesc)) {
                    div.innerHTML += `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 14px; height: 14px; background-color: ${color}; border: 1px solid #333; border-radius: 2px;"></div>
                            <span style="color: #555; font-size: 12px;">${description || "No Data"}</span>
                        </div>
                    `;
                }
                div.innerHTML += `</div>`;
                return div;
            };

            legend.addTo(map);
            return () => {
                legend.remove();
            };
        }, [map]);

        return null;
    };

    const bounds: [LatLngTuple, LatLngTuple] = [
        [18.7763, -179.1486], // Southwest corner (including Alaska & Hawaii)
        [71.5388001, -66.93457], // Northeast corner (continental US including Alaska)
    ];

    return (
        <div style={{ height: "500px", width: "100%", position: "relative" }}>
            {mapLoaded && (
                <MapContainer
                    center={[37.0902, -95.7129]} // Center of the US (approx.)
                    zoom={4}
                    maxZoom={10}
                    minZoom={4}
                    bounds={bounds}
                    style={{ height: "100%", width: "100%" }}
                    maxBounds={bounds}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
                    />

                    {geojsonData && (
                        <GeoJSON
                            data={geojsonData}
                            style={(feature) => {
                                if (!feature || !feature.properties) {
                                    return {
                                        fillColor: "#cccccc",
                                        weight: 2,
                                        opacity: 1,
                                        color: "white",
                                        dashArray: "3",
                                        fillOpacity: 0.7,
                                    };
                                }
                                const stateName = feature.properties.name;
                                const color = getStateColor(stateName);
                                return {
                                    fillColor: color,
                                    weight: 2,
                                    opacity: 1,
                                    color: "white",
                                    dashArray: "3",
                                    fillOpacity: 0.7,
                                };
                            }}
                        />
                    )}
                    {/* Add the legend */}
                    <Legend />
                </MapContainer>
            )}
            {!mapLoaded && <div>Loading map...</div>}
        </div>
    );
};

export default USAbortionMap;
