import { useState } from 'react';
import './App.css';
import HondaExtractor from './components/HondaExtractor';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-red-600 text-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold">Honda 360° Extractor</h1>
        <p className="text-red-100 mt-2">Sistema completo de extracción y visualización 360°</p>
      </header>
      <main className="container mx-auto px-4 py-8">
        <HondaExtractor />
      </main>
    </div>
  );
}

export default App;