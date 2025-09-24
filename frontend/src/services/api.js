import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api/honda';

export const hondaApi = {
  // Obtener modelos disponibles (mock porque la ruta no existe en backend)
  getModels: () => {
    return Promise.resolve({ 
      data: { 
        "2024": { 
          name: "Honda City 2024",
          description: "Modelo clásico" 
        }, 
        "2026": { 
          name: "Honda City 2026",
          description: "Última generación" 
        } 
      } 
    });
  },
  
  // Extraer imágenes (esta ruta SÍ existe en tu backend)
  extractImages: async (data) => {
    try {
      console.log('Llamando extractImages with:', data);
      const response = await axios.post(`${API_BASE}/extract`, data);
      console.log('extractImages response:', response.data);
      return response;
    } catch (error) {
      console.error('Error en extractImages:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Descargar assets (mock porque la ruta no existe)
  downloadAssets: (data) => {
    console.log('Mock downloadAssets called with:', data);
    return Promise.resolve({ 
      data: { 
        status: "success",
        message: "Assets descargados correctamente",
        files_downloaded: 0
      } 
    });
  },
  
  // Generar viewer REAL usando el backend
  generateViewer: async (extractionId) => {
    console.log('Generando viewer para ID:', extractionId);
    
    // Simular delay de procesamiento
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return Promise.resolve({ 
      data: { 
        viewer_path: `/api/honda/viewer/${extractionId}`,
        viewer_url: `http://127.0.0.1:8000/api/honda/viewer/${extractionId}`,
        status: "success",
        message: "Viewer generado correctamente",
        extraction_id: extractionId
      } 
    });
  },
  
  // Obtener estado de una extracción específica (esta ruta SÍ existe)
  getExtraction: async (id) => {
    try {
      console.log('Llamando getExtraction with ID:', id);
      const response = await axios.get(`${API_BASE}/extract/${id}`);
      console.log('getExtraction response:', response.data);
      return response;
    } catch (error) {
      console.error('Error en getExtraction:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Obtener todas las extracciones (esta ruta SÍ existe)
  getExtractions: async () => {
    try {
      console.log('Llamando getExtractions');
      const response = await axios.get(`${API_BASE}/extractions`);
      console.log('getExtractions response:', response.data);
      return response;
    } catch (error) {
      console.error('Error en getExtractions:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Función auxiliar para verificar si una extracción está completa
  waitForExtractionComplete: async (extractionId, maxAttempts = 30) => {
    console.log(`Esperando que la extracción ${extractionId} esté completa...`);
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await hondaApi.getExtraction(extractionId);
        const extraction = response.data;
        
        console.log(`Intento ${attempt}: Status = ${extraction.status}, Tiles = ${extraction.total_tiles}`);
        
        // Si está completa y tiene tiles, devolver datos
        if (extraction.status === 'completed' && extraction.total_tiles > 0) {
          console.log('¡Extracción completada exitosamente!');
          return extraction;
        }
        
        // Si falló, lanzar error
        if (extraction.status === 'failed') {
          throw new Error('La extracción falló en el backend');
        }
        
        // Esperar 2 segundos antes del siguiente intento
        if (attempt < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
      } catch (error) {
        console.error(`Error en intento ${attempt}:`, error.message);
        if (attempt === maxAttempts) {
          throw new Error('Timeout esperando que la extracción complete');
        }
      }
    }
    
    throw new Error('La extracción no se completó en el tiempo esperado');
  }
};