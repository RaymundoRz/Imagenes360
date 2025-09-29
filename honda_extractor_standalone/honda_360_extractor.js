const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');

class Honda360Extractor {
    constructor() {
        this.extractedImages = new Set();
        this.level2Images = new Set();
        this.downloadPath = './honda_360_images/';
        this.browser = null;
        this.page = null;
    }

    async setup() {
        console.log('🔧 Configurando extractor Honda 360°...');
        
        // Crear directorio de descarga
        if (!fs.existsSync(this.downloadPath)) {
            fs.mkdirSync(this.downloadPath, { recursive: true });
            console.log(`📁 Directorio creado: ${this.downloadPath}`);
        }

        // Lanzar navegador
        this.browser = await puppeteer.launch({
            headless: false, // Cambia a true para modo invisible
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ],
            defaultViewport: { width: 1920, height: 1080 }
        });

        this.page = await this.browser.newPage();
        
        // Configurar User-Agent Honda
        await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36');
        
        // Interceptar network requests
        await this.page.setRequestInterception(true);
        this.page.on('request', this.handleRequest.bind(this));
        
        console.log('✅ Navegador configurado correctamente');
    }

    handleRequest(request) {
        const url = request.url();
        
        // Interceptar imágenes .jpg del 360° Honda
        if (url.includes('.jpg') && (
            url.includes('tiles/') || 
            url.includes('exteriorlevel2/') ||
            url.includes('column') ||
            url.includes('cf_') ||
            url.includes('l_')
        )) {
            console.log(`📥 Imagen detectada: ${path.basename(url)}`);
            this.extractedImages.add(url);
            
            // Detectar imágenes de alta resolución (level2)
            if (url.includes('exteriorlevel2/') || 
                url.includes('column') || 
                url.includes('cf_') ||
                (url.includes('l_') && !url.includes('l_2'))) {
                this.level2Images.add(url);
                console.log(`🎯 ¡LEVEL2 DETECTADA! ${path.basename(url)}`);
            }
        }
        
        request.continue();
    }

    async extractHonda360(hondaUrl) {
        console.log('🌐 Cargando página Honda 360°...');
        console.log(`🔗 URL: ${hondaUrl}`);
        
        try {
            // Cargar página Honda
            await this.page.goto(hondaUrl, { 
                waitUntil: 'networkidle2',
                timeout: 60000
            });

            // Esperar que el viewer se cargue
            console.log('⏳ Esperando que cargue el viewer...');
            await this.page.waitForSelector('object, .ggskin, #object2vr', { timeout: 30000 });
            console.log('✅ Honda 360° cargado');

            // PASO 1: Esperar carga inicial
            await this.page.waitForTimeout(5000);
            console.log(`📊 Imágenes básicas detectadas: ${this.extractedImages.size}`);

            // PASO 2: ACTIVAR EL TRIGGER - ZOOM CONTINUO SOSTENIDO
            console.log('🔍 ¡ACTIVANDO TRIGGER DE ZOOM CONTINUO!');
            
            await this.page.evaluate(() => {
                return new Promise((resolve) => {
                    console.log('🎮 Iniciando simulación de zoom continuo...');
                    
                    // Buscar elementos de zoom
                    let zoomInBtn = document.querySelector('[gg-id="zoomin"]') || 
                                   document.querySelector('.zoomin') ||
                                   document.querySelector('#zoomin');
                    
                    if (zoomInBtn) {
                        console.log('✅ Botón zoom encontrado');
                        
                        // Activar estado mousedown
                        const mouseDownEvent = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        zoomInBtn.dispatchEvent(mouseDownEvent);
                        
                        // Si existe el objeto skin, activar manualmente
                        if (window.skinObj && window.skinObj.elementMouseDown) {
                            window.skinObj.elementMouseDown['zoomin'] = true;
                            console.log('✅ Estado mousedown activado en skinObj');
                        }
                        
                        // ZOOM CONTINUO POR 8 SEGUNDOS
                        let zoomCount = 0;
                        const zoomInterval = setInterval(() => {
                            if (zoomCount < 80) { // 80 iteraciones = 8 segundos
                                // Método 1: Usar player si existe
                                if (window.player && window.player.changeFovLog) {
                                    window.player.changeFovLog(-1, true);
                                }
                                
                                // Método 2: Usar objeto skin
                                if (window.skinObj && window.skinObj.player && window.skinObj.player.changeFovLog) {
                                    window.skinObj.player.changeFovLog(-1, true);
                                }
                                
                                zoomCount++;
                                if (zoomCount % 10 === 0) {
                                    console.log(`🔍 Zoom continuo: ${zoomCount}/80 (${(zoomCount/80*100).toFixed(1)}%)`);
                                }
                            } else {
                                clearInterval(zoomInterval);
                                
                                // Desactivar mousedown
                                if (window.skinObj && window.skinObj.elementMouseDown) {
                                    window.skinObj.elementMouseDown['zoomin'] = false;
                                }
                                
                                const mouseUpEvent = new MouseEvent('mouseup', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                zoomInBtn.dispatchEvent(mouseUpEvent);
                                
                                console.log('🔍 ¡ZOOM CONTINUO COMPLETADO!');
                                resolve();
                            }
                        }, 100); // Cada 100ms
                        
                    } else {
                        console.log('❌ No se encontró botón de zoom');
                        resolve();
                    }
                });
            });

            // Esperar que el zoom haga efecto
            console.log('⏳ Esperando efectos del zoom...');
            await this.page.waitForTimeout(3000);

            // PASO 3: EJECUTAR ROTACIÓN COMPLETA PARA ACTIVAR LEVEL2
            console.log('🔄 Ejecutando rotación completa para activar level2...');
            
            await this.page.evaluate(() => {
                return new Promise((resolve) => {
                    let panValue = 0;
                    const rotateInterval = setInterval(() => {
                        if (panValue <= 360) {
                            // Método 1: Usar player
                            if (window.player && window.player.changePan) {
                                window.player.changePan(panValue);
                            }
                            
                            // Método 2: Usar skinObj
                            if (window.skinObj && window.skinObj.player && window.skinObj.player.changePan) {
                                window.skinObj.player.changePan(panValue);
                            }
                            
                            panValue += 15;
                            if (panValue % 45 === 0) {
                                console.log(`🔄 Rotación: ${panValue}°`);
                            }
                        } else {
                            clearInterval(rotateInterval);
                            console.log('🔄 ¡ROTACIÓN COMPLETA FINALIZADA!');
                            resolve();
                        }
                    }, 200); // Cada 200ms
                });
            });

            // PASO 4: ESPERAR CARGA DE LEVEL2
            console.log('⏳ Esperando carga de imágenes level2...');
            await this.page.waitForTimeout(8000);
            
            // PASO 5: ROTACIÓN ADICIONAL PARA ASEGURAR TODAS LAS IMÁGENES
            console.log('🔄 Rotación adicional para completar level2...');
            await this.page.evaluate(() => {
                return new Promise((resolve) => {
                    let panValue = 0;
                    const finalRotateInterval = setInterval(() => {
                        if (panValue <= 720) { // 2 vueltas completas
                            if (window.player && window.player.changePan) {
                                window.player.changePan(panValue);
                            }
                            if (window.skinObj && window.skinObj.player && window.skinObj.player.changePan) {
                                window.skinObj.player.changePan(panValue);
                            }
                            panValue += 20;
                        } else {
                            clearInterval(finalRotateInterval);
                            console.log('🔄 Rotación final completada');
                            resolve();
                        }
                    }, 150);
                });
            });

            await this.page.waitForTimeout(5000);
            
            console.log('\n' + '='.repeat(60));
            console.log('📊 RESUMEN DE EXTRACCIÓN:');
            console.log(`📥 Total imágenes encontradas: ${this.extractedImages.size}`);
            console.log(`🎯 Imágenes level2 encontradas: ${this.level2Images.size}`);
            console.log('='.repeat(60));

            // PASO 6: DESCARGA MASIVA
            if (this.extractedImages.size > 0) {
                await this.downloadAllImages();
            } else {
                console.log('❌ No se encontraron imágenes para descargar');
            }

        } catch (error) {
            console.error('💥 Error durante la extracción:', error.message);
            throw error;
        }
    }

    async downloadAllImages() {
        console.log('\n💾 INICIANDO DESCARGA MASIVA...');
        console.log('='.repeat(60));
        
        const imageUrls = Array.from(this.extractedImages);
        let downloaded = 0;
        let failed = 0;
        let skipped = 0;

        for (let i = 0; i < imageUrls.length; i++) {
            const url = imageUrls[i];
            try {
                const filename = this.getFilenameFromUrl(url);
                const filepath = path.join(this.downloadPath, filename);
                
                if (!fs.existsSync(filepath)) {
                    await this.downloadFile(url, filepath);
                    downloaded++;
                    
                    const isLevel2 = this.level2Images.has(url) ? '🎯' : '📷';
                    console.log(`${isLevel2} ${downloaded}/${imageUrls.length}: ${filename}`);
                } else {
                    skipped++;
                    console.log(`⚠️ Ya existe: ${path.basename(filepath)}`);
                }
                
                // Progreso cada 10 archivos
                if ((downloaded + failed + skipped) % 10 === 0) {
                    const progress = ((downloaded + failed + skipped) / imageUrls.length * 100).toFixed(1);
                    console.log(`📈 Progreso: ${progress}% (${downloaded} OK, ${failed} ERROR, ${skipped} SKIP)`);
                }
                
            } catch (error) {
                failed++;
                console.log(`❌ Error descargando: ${path.basename(url)} - ${error.message}`);
            }
        }

        console.log('\n' + '='.repeat(60));
        console.log('🎉 DESCARGA COMPLETADA:');
        console.log(`✅ Descargadas: ${downloaded}`);
        console.log(`⚠️ Ya existían: ${skipped}`);
        console.log(`❌ Errores: ${failed}`);
        console.log(`📁 Ubicación: ${path.resolve(this.downloadPath)}`);
        console.log(`🎯 Level2 descargadas: ${Array.from(this.level2Images).filter(url => {
            const filename = this.getFilenameFromUrl(url);
            return fs.existsSync(path.join(this.downloadPath, filename));
        }).length}`);
        console.log('='.repeat(60));
    }

    getFilenameFromUrl(url) {
        // Extraer nombre de archivo de la URL
        const urlParts = url.split('/');
        const filename = urlParts[urlParts.length - 1];
        
        // Limpiar parámetros de query
        const cleanFilename = filename.split('?')[0];
        
        // Agregar prefijo para organizar
        if (this.level2Images.has(url)) {
            return `level2_${cleanFilename}`;
        } else {
            return `basic_${cleanFilename}`;
        }
    }

    downloadFile(url, filepath) {
        return new Promise((resolve, reject) => {
            const file = fs.createWriteStream(filepath);
            
            const request = https.get(url, (response) => {
                if (response.statusCode !== 200) {
                    file.close();
                    fs.unlink(filepath, () => {});
                    reject(new Error(`HTTP ${response.statusCode}`));
                    return;
                }
                
                response.pipe(file);
                
                file.on('finish', () => {
                    file.close();
                    resolve();
                });
                
            });
            
            request.on('error', (err) => {
                file.close();
                fs.unlink(filepath, () => {});
                reject(err);
            });
            
            file.on('error', (err) => {
                fs.unlink(filepath, () => {});
                reject(err);
            });
        });
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔧 Navegador cerrado');
        }
    }
}

// FUNCIÓN PRINCIPAL DE EJECUCIÓN
async function main() {
    const extractor = new Honda360Extractor();
    
    try {
        console.log('🚀 HONDA 360° EXTRACTOR AUTOMÁTICO');
        console.log('='.repeat(60));
        console.log('Basado en el análisis del trigger de zoom continuo');
        console.log('Desarrollado para resolver el misterio de las 600+ imágenes');
        console.log('='.repeat(60));
        
        await extractor.setup();
        
        // CONFIGURAR TU URL HONDA AQUÍ:
        const hondaUrl = 'https://www.honda.mx/autos/city/2026/exteriorlevel2/'; // ⚠️ CAMBIAR POR TU URL REAL
        
        console.log('⚠️ IMPORTANTE: Asegúrate de cambiar la URL en la línea anterior');
        console.log('📝 Reemplaza con la URL real de tu Honda 360°\n');
        
        await extractor.extractHonda360(hondaUrl);
        
    } catch (error) {
        console.error('💥 Error crítico:', error);
        console.log('\n🔧 SOLUCIONES POSIBLES:');
        console.log('1. Verificar que la URL sea correcta');
        console.log('2. Comprobar conexión a internet');
        console.log('3. Intentar con headless: true en puppeteer.launch()');
        console.log('4. Verificar que Honda 360° esté cargando correctamente');
    } finally {
        await extractor.cleanup();
    }
}

// AUTO-EJECUCIÓN
if (require.main === module) {
    main().then(() => {
        console.log('\n🎉 ¡EXTRACCIÓN HONDA 360° FINALIZADA!');
        process.exit(0);
    }).catch((error) => {
        console.error('💥 Error final:', error);
        process.exit(1);
    });
}

module.exports = Honda360Extractor;
