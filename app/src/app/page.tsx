"use client";

import { useState } from "react";
import USMap from "../components/MapComponent";

export default function Component() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-pink-500 to-orange-300"> 
      <h1 className="text-4xl font-bold text-center text-white mb-6">
        Ranking Women-Friendly States
      </h1>

      {/* Map Container */}
      <div className="w-full max-w-4xl shadow-lg rounded-lg bg-white overflow-hidden">
        <USMap />
      </div>

      {/* Optional description or footer */}
      <div className="mt-8 text-center text-white">
        {/* Add your description or footer here */}
      </div>
    </div>
  );
}