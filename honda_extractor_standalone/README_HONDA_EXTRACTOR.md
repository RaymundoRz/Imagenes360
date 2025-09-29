# 🚀 HONDA 360° EXTRACTOR AUTOMÁTICO

## 📋 DESCRIPCIÓN
Extractor automático basado en el descubrimiento del **trigger de zoom continuo** que activa la carga de imágenes `exteriorlevel2/` en Honda 360°.

## 🎯 MECANISMO IDENTIFICADO
- **Trigger Real**: Zoom continuo sostenido (no solo zoom + rotación)
- **Función**: `changeFovLog(-1, true)` ejecutada repetidamente cada 10ms
- **Resultado**: Activación automática de `exteriorlevel2/` después de 8 segundos
- **Imágenes**: 600+ imágenes de alta resolución

## 🛠️ INSTALACIÓN

### 1. Instalar Dependencias
```bash
npm install
```

### 2. Configurar URL Honda
Editar línea 71 en `honda_360_extractor.js`:
```javascript
const hondaUrl = 'TU_URL_REAL_DE_HONDA_360°';
```

### 3. Ejecutar Extractor
```bash
npm start
# o
node honda_360_extractor.js
```

## 🎮 FUNCIONAMIENTO

### PASO 1: Carga Inicial
- Carga la página Honda 360°
- Espera que el viewer se inicialice
- Intercepta requests de imágenes básicas

### PASO 2: Zoom Continuo (TRIGGER)
- Simula `mousedown` sostenido en botón zoom
- Ejecuta `changeFovLog(-1, true)` por 8 segundos
- Activa el estado `elementMouseDown['zoomin'] = true`

### PASO 3: Rotación Completa
- Rotación 360° para activar todas las imágenes level2
- Rotación adicional de 720° (2 vueltas)
- Asegura carga de todas las imágenes

### PASO 4: Descarga Masiva
- Descarga automática de todas las imágenes interceptadas
- Organización: `basic_*.jpg` y `level2_*.jpg`
- Prevención de duplicados

## 📊 RESULTADOS ESPERADOS

```
📁 honda_360_images/
├── basic_*.jpg (~64-128 imágenes básicas)
└── level2_*.jpg (~600+ imágenes alta resolución)
```

## 🔧 CONFIGURACIÓN AVANZADA

### Modo Headless
```javascript
headless: true  // Cambiar en puppeteer.launch()
```

### Timeouts Personalizados
```javascript
timeout: 60000  // 60 segundos para carga
```

### Selectores Personalizados
```javascript
await this.page.waitForSelector('object, .ggskin, #object2vr');
```

## 🚨 SOLUCIONES A PROBLEMAS

### Error: "Waiting for selector failed"
1. Verificar que la URL sea correcta
2. Comprobar conexión a internet
3. Intentar con `headless: true`
4. Verificar que Honda 360° esté cargando

### Error: "No se encontró botón de zoom"
1. Verificar que la página esté completamente cargada
2. Comprobar que el viewer Honda esté activo
3. Revisar selectores en el código

### Error: "No se encontraron imágenes"
1. Verificar que el zoom continuo se ejecute
2. Comprobar que la rotación se complete
3. Revisar interceptación de requests

## 📈 MÉTRICAS DE ÉXITO

- ✅ **Imágenes Básicas**: 64-128 imágenes
- ✅ **Imágenes Level2**: 600+ imágenes
- ✅ **Tiempo Total**: ~30-45 segundos
- ✅ **Sin Errores 404**: Todas las imágenes descargadas

## 🎯 INTEGRACIÓN CON SISTEMA EXISTENTE

El extractor se puede integrar con el sistema actual:

1. **Reemplazar Selenium**: Usar Puppeteer en lugar de Selenium
2. **Mantener Estructura**: Conservar organización por calidades
3. **Assets Brutos**: Extraer archivos sin modificaciones
4. **Viewers Locales**: Generar viewers funcionales

## 📝 NOTAS TÉCNICAS

- **Puppeteer**: Automatización de Chrome
- **Interceptación**: Captura de requests de imágenes
- **Simulación**: Eventos de mouse y teclado
- **Descarga**: HTTPS requests para imágenes
- **Organización**: Prefijos para diferentes niveles

## 🎉 RESULTADO FINAL

Sistema completamente automatizado que resuelve el misterio de las 600+ imágenes de Honda 360°, basado en el análisis del código JavaScript real de `object2vr_player.js` y `skin.js`.

---
**Desarrollado para resolver el problema de extracción de imágenes level2 en Honda 360°** 🚗✨
