"use client";

import { useState } from "react";
import USMedicaidMap from "../components/MedicaidMapComponent";
import USMap from "../components/MapComponent";
import USAbortionMap from "../components/AbortionMapComponent";

export default function Component() {
  const [selectedMap, setSelectedMap] = useState<string>("Overall");

  const handleMapChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedMap(event.target.value);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-pink-500 to-orange-300">
      <h1 className="text-4xl font-bold text-center text-white mb-6">
        Ranking Women and LGBTQ Friendly States
      </h1>

      {/* Dropdown for map selection */}
      <div className="mb-4">
        <label htmlFor="map-selector" className="text-white font-medium mr-4">
          Select Map:
        </label>
        <select
        id="map-selector"
        value={selectedMap}
        onChange={handleMapChange}
        className="px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-gray-800 font-medium hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-pink-500"
      >
        <option value="Overall" className="bg-white text-gray-800 hover:bg-gray-200">
          🌍 Overall
        </option>
        <option
          value="Medicaid"
          className="bg-white text-gray-800 hover:bg-gray-200"
        >
          🏥 State Medicaid Funds for Abortion
        </option>
          <option
          value="Abortion"
          className="bg-white text-gray-800 hover:bg-gray-200"
        >
          💉 Abortion Status
        </option>
      </select>
      </div>

      {/* Conditionally render the map */}
      <div className="w-full max-w-4xl shadow-lg rounded-lg bg-white overflow-hidden">
        {selectedMap === "Medicaid" ? (
          <USMedicaidMap />
        ) : selectedMap === "Abortion" ? (
          <USAbortionMap/>
        ) : (
          <USMap/>
        )}
      </div>

      {/* Optional description or footer */}
      <div className="mt-8 text-center text-white">
        {/* Add your description or footer here */}
      </div>
    </div>
  );
}
