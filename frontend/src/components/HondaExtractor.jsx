import { useState, useEffect } from 'react';
import { Download, Play, Eye, Settings, Loader2, CheckCircle, AlertCircle, Car, Zap, Star, Trophy } from 'lucide-react';
import { hondaApi } from '../services/api';

const HondaExtractor = () => {
  const [selectedYear, setSelectedYear] = useState('2026');
  const [selectedQualities, setSelectedQualities] = useState({
    interior: { quality0: true, quality1: true, quality2: true },
    exterior: { quality0: true, quality1: true, quality2: true }
  });
  const [selectedViews, setSelectedViews] = useState({
    interior: true,
    exterior: true
  });
  const [downloadStatus, setDownloadStatus] = useState({});
  const [isDownloading, setIsDownloading] = useState(false);
  const [completedDownloads, setCompletedDownloads] = useState({});

  // Información de calidades con estilo Honda
  const qualityInfo = {
    quality0: { 
      name: 'Ultra HD', 
      badge: 'PREMIUM',
      resolution: '5200×1900', 
      size: '~80MB', 
      tiles: '384+', 
      desc: 'Máxima calidad con zoom extremo',
      color: 'from-purple-600 to-purple-800',
      icon: Trophy
    },
    quality1: { 
      name: 'High Definition', 
      badge: 'POPULAR',
      resolution: '2600×950', 
      size: '~25MB', 
      tiles: '96+', 
      desc: 'Balance perfecto calidad/velocidad',
      color: 'from-blue-600 to-blue-800',
      icon: Star
    },
    quality2: { 
      name: 'Standard', 
      badge: 'RÁPIDO',
      resolution: '1300×475', 
      size: '~5MB', 
      tiles: '24+', 
      desc: 'Carga rápida, ideal para móviles',
      color: 'from-green-600 to-green-800',
      icon: Zap
    }
  };

  const handleDownloadAll = async () => {
    setIsDownloading(true);
    setDownloadStatus({});
    setCompletedDownloads({});

    const tasks = [];
    
    // Generar tareas correctamente
    Object.entries(selectedViews).forEach(([viewType, isSelected]) => {
      if (isSelected) {
        Object.entries(selectedQualities[viewType]).forEach(([quality, isQualitySelected]) => {
          if (isQualitySelected) {
            const qualityLevel = parseInt(quality.replace('quality', ''));
            tasks.push({
              id: `${viewType}_${quality}`,
              year: selectedYear,
              view_type: viewType,
              quality_level: qualityLevel,
              name: `${viewType === 'interior' ? 'Interior' : 'Exterior'} ${qualityInfo[quality].name}`
            });
          }
        });
      }
    });

    console.log("Tareas generadas:", tasks); // Debug

    // Ejecutar tareas
    for (const task of tasks) {
      try {
        setDownloadStatus(prev => ({ ...prev, [task.id]: 'downloading' }));

        console.log("Enviando datos:", {
          year: task.year,
          view_type: task.view_type,
          quality_level: task.quality_level
        }); // Debug

        // 1. Extraer imágenes CON DATOS CORRECTOS
        const extractResponse = await hondaApi.extractImages({
          year: task.year,
          view_type: task.view_type,
          quality_level: task.quality_level
        });

        console.log("Respuesta extracción:", extractResponse.data); // Debug

        const extractionId = extractResponse.data.extraction_id || `mock_${Date.now()}`;

        // 2. Simular descarga de assets
        await hondaApi.downloadAssets({
          year: task.year,
          view_type: task.view_type,
          quality_level: task.quality_level
        });

        // 3. Generar viewer
        const viewerResponse = await hondaApi.generateViewer(extractionId);

        setDownloadStatus(prev => ({ ...prev, [task.id]: 'completed' }));
        setCompletedDownloads(prev => ({ 
          ...prev, 
          [task.id]: {
            ...task,
            extractionId,
            viewerPath: viewerResponse.data.viewer_path
          }
        }));

      } catch (error) {
        console.error(`Error descargando ${task.name}:`, error);
        console.error("Error details:", error.response?.data); // Debug detallado
        setDownloadStatus(prev => ({ ...prev, [task.id]: 'error' }));
      }
    }

    setIsDownloading(false);
  };

  const openViewer = (viewerPath, completedDownload) => {
    const year = completedDownload.year;
    const viewType = completedDownload.view_type.toUpperCase();
    
    // URL dinámica correcta basada en ViewType
    const viewerUrl = `http://127.0.0.1:8080/honda_city_${year}/ViewType.${viewType}/viewer.html`;
    
    console.log(`🎯 Abriendo viewer: ${completedDownload.name}`, {
      url: viewerUrl,
      viewType,
      quality: completedDownload.quality_level
    });
    
    window.open(viewerUrl, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-red-600 via-red-700 to-red-800 text-white shadow-2xl">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center gap-6 mb-6">
            <div className="p-4 bg-white bg-opacity-20 rounded-2xl backdrop-blur-sm">
              <Car className="w-12 h-12" />
            </div>
            <div>
              <h1 className="text-5xl font-bold mb-2">Honda 360° Extractor</h1>
              <p className="text-red-100 text-xl">Sistema profesional de extracción y visualización 360°</p>
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
            {[
              { label: 'Modelos', value: '2', icon: Car },
              { label: 'Calidades', value: '3', icon: Star },
              { label: 'Resolución Max', value: '5200px', icon: Eye },
              { label: 'Tecnología', value: '360°', icon: Settings }
            ].map((stat, i) => (
              <div key={i} className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-4 text-center">
                <stat.icon className="w-8 h-8 mx-auto mb-2 text-red-200" />
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-red-200 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 space-y-12">
        
        {/* Selector de Modelo */}
        <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
          <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <Car className="w-8 h-8 text-red-600" />
            Seleccionar Modelo Honda City
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {['2024', '2026'].map(year => (
              <button
                key={year}
                onClick={() => setSelectedYear(year)}
                className={`group relative overflow-hidden rounded-2xl p-8 transition-all duration-300 transform hover:scale-105 ${
                  selectedYear === year
                    ? 'bg-gradient-to-r from-red-600 to-red-700 text-white shadow-2xl'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border-2 border-gray-200'
                }`}
              >
                <div className="relative z-10">
                  <div className="text-3xl font-bold mb-2">Honda City {year}</div>
                  <div className="text-lg opacity-90">
                    {year === '2026' ? 'Última generación' : 'Modelo clásico'}
                  </div>
                  {selectedYear === year && (
                    <div className="absolute top-4 right-4">
                      <CheckCircle className="w-8 h-8" />
                    </div>
                  )}
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white opacity-10"></div>
              </button>
            ))}
          </div>
        </div>

        {/* Selector de Vistas */}
        <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Experiencia 360° Disponible</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              { 
                key: 'interior', 
                label: 'Interior 360°', 
                emoji: '🏠', 
                tech: 'Pano2VR Technology',
                desc: 'Explora cada detalle del interior con rotación completa',
                gradient: 'from-blue-500 to-blue-700'
              },
              { 
                key: 'exterior', 
                label: 'Exterior 360°', 
                emoji: '🚗', 
                tech: 'Object2VR Technology',
                desc: 'Rota el vehículo para ver todos los ángulos externos',
                gradient: 'from-red-500 to-red-700'
              }
            ].map(view => (
              <div
                key={view.key}
                onClick={() => setSelectedViews(prev => ({ ...prev, [view.key]: !prev[view.key] }))}
                className={`group cursor-pointer rounded-2xl p-8 transition-all duration-300 transform hover:scale-105 ${
                  selectedViews[view.key]
                    ? `bg-gradient-to-r ${view.gradient} text-white shadow-2xl`
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <span className="text-4xl mb-4 block">{view.emoji}</span>
                  {selectedViews[view.key] && (
                    <CheckCircle className="w-8 h-8 text-white" />
                  )}
                </div>
                
                <h3 className="text-2xl font-bold mb-2">{view.label}</h3>
                <p className="text-lg opacity-90 mb-3">{view.tech}</p>
                <p className={`text-sm ${selectedViews[view.key] ? 'text-white opacity-90' : 'text-gray-600'}`}>
                  {view.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Selector de Calidades Premium */}
        <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Calidades de Imagen</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {Object.entries(qualityInfo).map(([qualityKey, info]) => {
              const IconComponent = info.icon;
              return (
                <div key={qualityKey} className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${info.color} text-white p-8 shadow-xl`}>
                  
                  {/* Badge */}
                  <div className="absolute top-4 right-4 bg-white bg-opacity-20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold">
                    {info.badge}
                  </div>
                  
                  {/* Icon */}
                  <IconComponent className="w-12 h-12 mb-6 opacity-80" />
                  
                  {/* Content */}
                  <h3 className="text-2xl font-bold mb-2">{info.name}</h3>
                  <p className="text-white opacity-90 mb-4">{info.desc}</p>
                  
                  {/* Stats */}
                  <div className="space-y-2 mb-6">
                    <div className="flex justify-between">
                      <span className="opacity-80">Resolución:</span>
                      <span className="font-bold">{info.resolution}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="opacity-80">Tamaño:</span>
                      <span className="font-bold">{info.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="opacity-80">Tiles:</span>
                      <span className="font-bold">{info.tiles}</span>
                    </div>
                  </div>
                  
                  {/* Checkboxes */}
                  <div className="space-y-3">
                    {Object.entries(selectedViews).map(([viewType, isViewSelected]) => (
                      isViewSelected && (
                        <label key={viewType} className="flex items-center gap-3 cursor-pointer bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-3">
                          <input
                            type="checkbox"
                            checked={selectedQualities[viewType][qualityKey]}
                            onChange={(e) => setSelectedQualities(prev => ({
                              ...prev,
                              [viewType]: { ...prev[viewType], [qualityKey]: e.target.checked }
                            }))}
                            className="w-5 h-5 rounded border-white bg-transparent accent-white"
                          />
                          <span className="font-medium">
                            {viewType === 'interior' ? '🏠 Interior' : '🚗 Exterior'}
                          </span>
                        </label>
                      )
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Botón de Descarga Premium */}
        <div className="text-center py-8">
          <button
            onClick={handleDownloadAll}
            disabled={isDownloading}
            className={`group relative overflow-hidden px-12 py-6 rounded-2xl text-white font-bold text-xl transition-all duration-300 transform hover:scale-105 ${
              isDownloading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-red-600 via-red-700 to-red-800 hover:from-red-700 hover:via-red-800 hover:to-red-900 shadow-2xl hover:shadow-red-500/25'
            }`}
          >
            <div className="relative z-10 flex items-center gap-4">
              {isDownloading ? (
                <>
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <span>Descargando Honda 360°...</span>
                </>
              ) : (
                <>
                  <Download className="w-8 h-8" />
                  <span>Descargar Todo Seleccionado</span>
                </>
              )}
            </div>
            
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
          </button>
        </div>

        {/* Estado de Descargas con estilo premium */}
        {Object.keys(downloadStatus).length > 0 && (
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Estado de Descargas</h3>
            <div className="space-y-4">
              {Object.entries(downloadStatus).map(([taskId, status]) => (
                <div key={taskId} className="flex items-center justify-between p-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
                  <span className="font-bold text-lg">{taskId.replace('_', ' ').toUpperCase()}</span>
                  <div className="flex items-center gap-3">
                    {status === 'downloading' && <Loader2 className="w-6 h-6 animate-spin text-blue-500" />}
                    {status === 'completed' && <CheckCircle className="w-6 h-6 text-green-500" />}
                    {status === 'error' && <AlertCircle className="w-6 h-6 text-red-500" />}
                    <span className="text-lg font-medium capitalize">{status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Visualizadores Premium */}
        {Object.keys(completedDownloads).length > 0 && (
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">🎮 Visualizadores 360° Listos</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(completedDownloads).map(([taskId, download]) => (
                <div key={taskId} className="group bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-200 rounded-2xl p-6 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-3xl">{download.view_type === 'interior' ? '🏠' : '🚗'}</span>
                    <div>
                      <h4 className="font-bold text-lg text-gray-800">{download.name}</h4>
                      <p className="text-green-700">Honda City {download.year}</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => openViewer(download.viewerPath, download)}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-700 hover:from-green-700 hover:to-emerald-800 text-white py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 shadow-lg group-hover:shadow-xl"
                  >
                    <Play className="w-5 h-5" />
                    Abrir Visualizador 360°
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default HondaExtractor;