# 🧠 AI Microservices Suite (Monorepo)

Suite unificada de microservicios de Inteligencia Artificial que opera de forma local sobre Linux (CachyOS), potenciada por **FastAPI**, **Ollama (Qwen 2.5 7B)**, **Faster-Whisper**, **ChromaDB**, **Typst**, **yt-dlp**, monitor de hardware e integración nativa con **Obsidian**.

---

## 🌐 Gateway Centralizada (FastAPI Hub)

* **Servidor**: `http://localhost:8080`
* **Swagger UI Interactivo**: [http://localhost:8080/docs](http://localhost:8080/docs)
* **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

---

## 🛠️ Catálogo Completo de los 19 Microservicios

### 📦 Bloque A: Productividad de Contenidos y Documentos
| # | Microservicio | Endpoint | Descripción |
|---|---|---|---|
| **1** | **Transcripción Audio** | `POST /transcription/audio` | Transcribe notas de voz/reuniones con Whisper y resume compromisos clave. |
| **2** | **Búsqueda Semántica** | `POST /search/index`<br>`POST /search/query` | Base de conocimiento RAG local con ChromaDB para buscar por concepto. |
| **3** | **Corrección y Tono** | `POST /text/enhance` | Modos: `proofread`, `formalize`, `concise`, `academic` y `translate`. |
| **4** | **Lector Web Limpio** | `POST /web/extract` | Extrae artículos de blogs/noticias sin publicidad a Markdown con síntesis. |
| **5** | **Diagnóstico de Errores** | `POST /diagnostics/explain-error` | Diagnostica stack traces, fallos de Docker o Linux y da comandos de solución. |
| **6** | **Texto a Voz (TTS)** | `POST /tts/synthesize` | Convierte texto a audio `.mp3` descargable con voz en español/inglés. |
| **7** | **Organizador Inteligente** | `POST /organizer/suggest-name` | Sugiere nombres canónicos normalizados y categorías para archivos desordenados. |
| **8** | **Monitor de Hardware** | `GET /system/resources`<br>`POST /system/free-vram` | Muestra uso en tiempo real de RAM (psutil), Swap y VRAM GPU NVIDIA con liberación de memoria. |

### ⚡ Bloque B: Multimedia, DevOps, Seguridad y Automatización Avanzada
| # | Microservicio | Endpoint | Descripción |
|---|---|---|---|
| **9** | **Resumen de YouTube** | `POST /youtube/summarize` | Descarga el audio de cualquier video, lo transcribe y extrae sus puntos clave. |
| **10** | **Copilot de Terminal Bash** | `POST /terminal/generate-command` | Genera comandos Bash exactos y evalúa niveles de riesgo (`safe`, `dangerous`). |
| **11** | **Redactor de Correos** | `POST /email/draft-reply` | Crea correos ejecutivos o respuestas a partir de notas breves y un tono seleccionado. |
| **12** | **Tests Unitarios & Docs** | `POST /code/generate-tests` | Genera suites de PyTest/Jest exhaustivas y docstrings tipados para tu código. |
| **13** | **Anonimización PII** | `POST /security/anonymize` | Reemplaza nombres, emails, tarjetas, IPs y claves por tokens seguros antes de compartir. |
| **14** | **Extractor de Facturas** | `POST /finance/extract-receipt` | Convierte el texto de un ticket/factura en un JSON contable normalizado con ítems. |
| **15** | **Clonación / Perfiles de Voz** | `POST /voice/register-profile`<br>`POST /voice/synthesize-cloned` | Registra muestras de audio y sintetiza texto con perfiles de voz asignados. |
| **16** | **Generador de Podcasts** | `POST /podcast/generate-script` | Crea guiones dinámicos a 2 voces (Alex y Sam) debatiendo cualquier tema (NotebookLM). |
| **17** | **Scraping Dinámico** | `POST /browser/extract-structured` | Extrae campos específicos (precios, stock, tablas) de páginas web a JSON. |
| **18** | **Forense de Imágenes** | `POST /forensics/analyze-image` | Inspecciona metadatos EXIF y firmas de difusión para evaluar si es foto real o IA. |

### 🧠 Bloque C: Gestión del Conocimiento Personal (PKM)
| # | Microservicio | Endpoint | Descripción |
|---|---|---|---|
| **19** | **Puente Obsidian (PKM)** | `GET /obsidian/vaults`<br>`POST /obsidian/create-note` | Genera notas con Frontmatter YAML y `[[WikiLinks]]`, guardándolas directamente en tus Vaults (**MiCerebro** o **Maestría**). |

---

## 📂 Directorio de Servicios del Sistema

| Módulo | Tipo | Estado | Puerto / Ubicación |
| :--- | :--- | :--- | :--- |
| [`gateway/`](./gateway) | API Systemd | 🟢 Activo | `http://localhost:8080` (Unifica los 21 microservicios con Swagger en `/docs`) |
| [`doc_summarizer/`](./doc_summarizer) | Daemon Systemd | 🟢 Activo | Monitorea `~/Downloads`, extrae a Markdown y compila resúmenes APA 7 |

---

## 🔄 Control de Servicios (`systemd`)

```bash
# Gateway Centralizada (Los 21 Microservicios)
systemctl --user status ai-gateway.service
systemctl --user restart ai-gateway.service

# Vigilante de Descargas (Resumidor APA 7)
systemctl --user status doc-summarizer.service
systemctl --user restart doc-summarizer.service
```
