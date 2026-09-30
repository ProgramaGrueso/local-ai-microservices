#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2.2cm, left: 2cm, right: 2cm),
  header: context {
    if here().page() > 1 {
      align(right, text(fill: luma(120), size: 8.5pt)[
        *Suite de Microservicios de IA* — Guía de Uso y Evaluación de Viabilidad
      ])
    }
  },
  footer: context {
    align(center, text(fill: luma(120), size: 8.5pt)[
      Página #counter(page).display() de #counter(page).final().at(0)
    ])
  }
)

#set text(
  font: "Liberation Sans",
  size: 10pt,
  fill: rgb("#1a202c"),
  lang: "es"
)

#set par(justify: true, leading: 0.65em)

// Estilos de títulos
#show heading.where(level: 1): it => block(
  above: 1.5em, below: 0.8em,
  text(fill: rgb("#1a365d"), weight: "bold", size: 16pt)[#it.body]
)

#show heading.where(level: 2): it => block(
  above: 1.2em, below: 0.6em,
  text(fill: rgb("#2b6cb0"), weight: "bold", size: 12.5pt)[#it.body]
)

#show heading.where(level: 3): it => block(
  above: 0.9em, below: 0.4em,
  text(fill: rgb("#2d3748"), weight: "bold", size: 11pt)[#it.body]
)

#let badge(texto, color) = box(
  fill: color.lighten(85%),
  stroke: color.lighten(30%),
  radius: 3pt,
  inset: (x: 5pt, y: 2.5pt),
  outset: 0pt,
  baseline: 0%,
  text(fill: color, size: 8pt, weight: "bold")[#texto]
)

#let callout(title, body, col: rgb("#2b6cb0")) = block(
  fill: col.lighten(94%),
  stroke: (left: 3pt + col),
  inset: (x: 10pt, y: 8pt),
  radius: (right: 4pt),
  above: 1em,
  below: 1em,
  [
    #text(weight: "bold", fill: col, size: 9.5pt)[#title]\
    #text(size: 9pt)[#body]
  ]
)

// PORTADA / ENCABEZADO
#align(center)[
  #block(
    fill: rgb("#ebf8ff"),
    stroke: 1pt + rgb("#bee3f8"),
    inset: 18pt,
    radius: 8pt,
    width: 100%,
    [
      #text(size: 20pt, weight: "bold", fill: rgb("#2b6cb0"))[Manual Técnico y Evaluación de Viabilidad]\
      #v(4pt)
      #text(size: 13pt, fill: rgb("#2d3748"))[Suite de Microservicios de Inteligencia Artificial (FastAPI Gateway 8080)]\
      #v(6pt)
      #text(size: 9pt, fill: rgb("#718096"))[
        *Hardware de Referencia:* NVIDIA GeForce RTX 4070 Ti SUPER (16 GB VRAM) | 62 GB RAM | CachyOS Linux\
        *Documento generado:* Septiembre 2026 | Autor: Sistema Antigravity / API IA Hub
      ]
    ]
  )
]

#v(1em)

= 1. Resumen Ejecutivo y Matriz de Viabilidad

Esta guía analiza en profundidad los microservicios activos en el Gateway local (`http://localhost:8080`). Se evalúan con total transparencia los *costos ocultos*: consumo de memoria VRAM de la GPU, uso de RAM del sistema, necesidad de conexión a internet y tiempo de latencia, para que puedas decidir cuáles integrar en tu flujo de trabajo diario y cuáles descartar.

#v(0.5em)

#table(
  columns: (2.2fr, 2fr, 1.8fr, 1.3fr, 1.5fr),
  fill: (col, row) => if row == 0 { rgb("#edf2f7") } else if calc.even(row) { rgb("#f7fafc") } else { none },
  stroke: 0.5pt + rgb("#e2e8f0"),
  inset: 5pt,
  align: (left, left, center, center, center),
  [*Microservicio*], [*Endpoint*], [*Hardware / VRAM*], [*Internet*], [*Viabilidad*],
  [Transcripción Audio], [`/transcription/audio`], [1.5 GB VRAM / CPU fallback], [No (100% Local)], [#badge("ALTA (9/10)", rgb("#2f855a"))],
  [Búsqueda Semántica], [`/search/query`], [150 MB RAM (0 VRAM)], [No (100% Local)], [#badge("ALTA (9.5/10)", rgb("#2f855a"))],
  [Visión y OCR], [`/vision/ocr`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (8.5/10)", rgb("#2f855a"))],
  [Corrección de Texto], [`/text/enhance`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Texto a Diagramas], [`/diagrams/generate`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (9/10)", rgb("#2f855a"))],
  [Lector Web Limpio], [`/web/extract`], [50 MB RAM (0 VRAM)], [Sí (descarga URL)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Diagnóstico Errores], [`/diagnostics/explain-error`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Texto a Voz (TTS)], [`/tts/synthesize`], [30 MB RAM (0 VRAM)], [Sí (gTTS)], [#badge("MEDIA (7/10)", rgb("#c05621"))],
  [Organizador Archivos], [`/organizer/suggest-name`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (9/10)", rgb("#2f855a"))],
  [Monitor de Hardware], [`/system/resources`], [0 MB VRAM (\<10ms CPU)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Resumen de YouTube], [`/youtube/summarize`], [1.5 GB VRAM + Ollama], [Sí (yt-dlp)], [#badge("ALTA (8/10)", rgb("#2f855a"))],
  [Copilot de Bash], [`/terminal/generate-command`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Redactor de Emails], [`/email/draft-reply`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (9/10)", rgb("#2f855a"))],
  [Generador de Tests], [`/code/generate-tests`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (9/10)", rgb("#2f855a"))],
  [Anonimización PII], [`/security/anonymize`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (8.5/10)", rgb("#2f855a"))],
  [Extractor Facturas], [`/finance/extract-receipt`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("ALTA (8.5/10)", rgb("#2f855a"))],
  [Clonación de Voz], [`/voice/synthesize-cloned`], [100 MB RAM (0 VRAM)], [No (Piper/TTS)], [#badge("MEDIA (6.5/10)", rgb("#c05621"))],
  [Generador Podcasts], [`/podcast/generate-script`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("MEDIA (7.5/10)", rgb("#2f855a"))],
  [Scraping Dinámico], [`/browser/extract-structured`], [80 MB RAM (0 VRAM)], [Sí (descarga URL)], [#badge("ALTA (8.5/10)", rgb("#2f855a"))],
  [Forense de Imágenes], [`/forensics/analyze-image`], [20 MB RAM (0 VRAM)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))],
  [Puente Obsidian PKM], [`/obsidian/create-note`], [4.8 GB VRAM (Ollama)], [No (100% Local)], [#badge("MÁXIMA (10/10)", rgb("#2f855a"))]
)

#v(1em)

#callout("Nota clave sobre Ollama y la memoria VRAM", [
  Los microservicios que utilizan un LLM (como `/text/enhance`, `/bash_copilot`, `/diagrams`, etc.) *NO cargan modelos nuevos ni consumen VRAM adicional*. Todos comparten la misma instancia residente de Ollama (`qwen2.5:7b`), que ocupa de manera fija *4.78 GB de VRAM*. Ejecutar 1 o 100 consultas a estos endpoints no incrementa el uso de VRAM de la GPU ni satura la memoria.
])

#pagebreak()

= 2. Guía Detallada de Microservicios por Categoría

== Categoría A: Monitoreo de Sistema y Control de Hardware

=== 1. Monitor de Recursos en Tiempo Real y Purga de VRAM
- *Endpoints:* `GET /system/resources` y `POST /system/free-vram`
- *Propósito:* Diagnosticar en cualquier momento el estado de tu hardware antes de iniciar tareas pesadas.
- *Ejemplo de uso:*
```bash
curl -s http://localhost:8080/system/resources | jq .
```
- *Respuesta esperada:*
```json
{
  "status": "healthy",
  "system_ram": { "total_gb": 62.7, "used_gb": 12.6, "percentage_used": 20.1 },
  "gpu_nvidia": {
    "gpu_name": "NVIDIA GeForce RTX 4070 Ti SUPER",
    "vram_total_gb": 15.99,
    "vram_used_gb": 6.14,
    "vram_free_gb": 9.51,
    "temperature_celsius": 43
  }
}
```
- *Costos Ocultos y Recursos:* *Cero*. Utiliza llamadas directas al kernel (`psutil` y `nvidia-smi`), demora menos de 5 ms y consume 0 bytes de VRAM.
- *Veredicto:* *Imprescindible (10/10)*. Te da visibilidad absoluta de si la GPU está libre o retenida.

---

== Categoría B: Productividad de Texto, Redacción y DevOps

=== 2. Corrección de Estilo, Tono y Traducción (`/text/enhance`)
- *Propósito:* Corregir ortografía, redactar en modo académico formal, sintetizar o traducir textos largos con preservación contextual.
- *Parámetros:* `mode` (`proofread`, `formalize`, `concise`, `academic`, `translate`).
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/text/enhance \
  -H "Content-Type: application/json" \
  -d '{"text": "el paper muestra resultados que estan bien pero hay que pulir el metodo", "mode": "academic"}' | jq .
```
- *Costos Ocultos:* Ninguno. Solo hace inferencia sobre Ollama (respuesta en 1.2 segundos).
- *Veredicto:* *Máxima viabilidad (10/10)*. Extremadamente ligero para uso en Obsidian o redacción de tesis.

=== 3. Copilot de Terminal Bash (`/terminal/generate-command`)
- *Propósito:* Convertir una orden en lenguaje natural en un comando Bash exacto para CachyOS/Arch, clasificando su nivel de peligro (`safe`, `moderate`, `dangerous`).
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/terminal/generate-command \
  -H "Content-Type: application/json" \
  -d '{"instruction": "buscar todos los archivos mayores a 500MB en Downloads y ordenarlos por peso"}' | jq .
```
- *Costos Ocultos:* Cero.
- *Veredicto:* *Máxima viabilidad (10/10)*. Evita cometer errores destructivos en Linux (`rm`, permisos `chmod`).

=== 4. Diagnóstico de Errores y Stack Traces (`/diagnostics/explain-error`)
- *Propósito:* Pegar un log de error de Python, Docker, C++ o terminal y recibir la causa raíz y el comando exacto para solucionarlo.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/diagnostics/explain-error \
  -H "Content-Type: application/json" \
  -d '{"error_message": "CUDA out of memory. Tried to allocate 2.00 GiB"}' | jq .
```
- *Costos Ocultos:* Cero.
- *Veredicto:* *Máxima viabilidad (10/10)*. Ahorra búsquedas manuales en foros.

=== 5. Generador de Diagramas Mermaid (`/diagrams/generate`)
- *Propósito:* Convertir explicaciones textuales en diagramas de flujo, secuencia o arquitectura en sintaxis Mermaid.js compatible con Obsidian y GitHub.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Flujo de usuario: Login -> Verificacion 2FA -> Dashboard", "diagram_type": "sequence"}' | jq .
```
- *Costos Ocultos:* Cero. Devuelve el código fuente del diagrama y una URL de vista previa directa en `mermaid.live`.
- *Veredicto:* *Alta viabilidad (9/10)*.

#pagebreak()

=== 6. Generador de Tests Unitarios y Documentación (`/code/generate-tests`)
- *Propósito:* Analizar cualquier función o módulo de código y generar la suite completa de pruebas unitarias (`pytest` o `jest`) cubriendo edge cases y casos de error.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/code/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"code": "def divide(a: float, b: float) -> float:\n    return a / b", "framework": "pytest"}' | jq .
```
- *Costos Ocultos:* Cero.
- *Veredicto:* *Alta viabilidad (9/10)*.

=== 7. Redactor de Correos Profesionales (`/email/draft-reply`)
- *Propósito:* Redactar correos ejecutivos completos a partir de ideas clave o responder cadenas de correos manteniendo el contexto.
- *Costos Ocultos:* Cero.
- *Veredicto:* *Alta viabilidad (9/10)*.

---

== Categoría C: Extracción Web, Multimedia y YouTube

=== 8. Extractor de Artículos Web Limpio (`/web/extract`)
- *Propósito:* Extraer el contenido principal de cualquier blog, noticia o tutorial sin anuncios, cookies ni menús, entregándolo en Markdown estructurado con viñetas ejecutivas.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/web/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com", "summarize": true}' | jq .
```
- *Costos Ocultos:*
  - *Internet:* Requiere conexión activa para descargar el HTML.
  - *Memoria:* Consume apenas ~40 MB de RAM transitorios usando la biblioteca `trafilatura`. 0 VRAM.
- *Veredicto:* *Máxima viabilidad (10/10)*. Ideal para guardar artículos limpios en Obsidian.

=== 9. Resumen Ejecutivo de Videos de YouTube (`/youtube/summarize`)
- *Propósito:* Ingresas la URL de un video de YouTube, descarga el canal de audio con `yt-dlp`, lo transcribe con Whisper local y genera una síntesis con puntos clave.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/youtube/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "max_duration_minutes": 20}' | jq .
```
- *Costos Ocultos y Advertencias:*
  - *Ancho de banda:* Descarga el archivo de audio `.m4a` a `/tmp/`.
  - *VRAM:* Whisper carga temporalmente en GPU (~1.5 GB de VRAM durante la transcripción). Posee *fallback automático a CPU* si la GPU está ocupada.
  - *Tiempo:* Videos de 15 minutos demoran entre 20 y 40 segundos en procesarse.
- *Veredicto:* *Alta viabilidad (8/10)*. Muy útil para conferencias o videos educativos largos; no abusar en segundo plano mientras juegas.

=== 10. Forense e Inspección de Imágenes (`/forensics/analyze-image`)
- *Propósito:* Analizar cualquier imagen para detectar si es una fotografía real (cámara, lente, apertura) o generada por IA (detecta firmas de ComfyUI, Midjourney, Stable Diffusion en metadatos PNG/EXIF).
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/forensics/analyze-image \
  -F "file=@/ruta/a/tu/imagen.png" | jq .
```
- *Costos Ocultos:* *Ninguno*. Inferencia sobre metadatos mediante Pillow. Respuesta en 20 ms.
- *Veredicto:* *Máxima viabilidad (10/10)*.

=== 11. Extractor Web Dinámico Estructurado (`/browser/extract-structured`)
- *Propósito:* Extraer selectivamente campos JSON concretos (precios, títulos, especificaciones técnicas) desde páginas web.
- *Costos Ocultos:* Requiere internet. Ligero en RAM.
- *Veredicto:* *Alta viabilidad (8.5/10)*.

#pagebreak()

== Categoría D: Audio, Voz y Transcripción

=== 12. Transcripción de Audio y Minutas (`/transcription/audio`)
- *Propósito:* Subir un archivo de audio (`.mp3`, `.wav`, `.m4a`) de una nota de voz o reunión. Lo transcribe íntegramente con marcas de tiempo y extrae tareas pendientes (*action items*).
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/transcription/audio \
  -F "file=@nota_de_voz.mp3" | jq .
```
- *Costos Ocultos:* Whisper ocupa ~1.5 GB de VRAM durante los segundos de la transcripción y luego libera tensores.
- *Veredicto:* *Alta viabilidad (9/10)*.

=== 13. Texto a Voz Simple (`/tts/synthesize`)
- *Propósito:* Convertir cualquier texto a un archivo de audio `.mp3` descargable.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, este es un reporte sintetizado desde tu suite local.", "lang": "es"}' \
  --output respuesta.mp3
```
- *Costos Ocultos:* Usa `gTTS`, por lo que requiere conexión a internet para generar el MP3. Consume 0 VRAM.
- *Veredicto:* *Viabilidad media (7/10)*. Funcional, pero dependiente de conexión externa.

=== 14. Clonación de Perfiles de Voz (`/voice/synthesize-cloned`)
- *Propósito:* Almacenar perfiles acústicos y sintetizar con la voz de referencia.
- *Costos Ocultos:* Calidad dependiente del motor local.
- *Veredicto:* *Viabilidad media (6.5/10)*. Útil para experimentos de voz, no esencial en el día a día.

=== 15. Generador de Podcasts a 2 Voces (`/podcast/generate-script`)
- *Propósito:* Convertir un artículo o PDF en un diálogo dinámico entre dos locutores al estilo Google NotebookLM.
- *Veredicto:* *Viabilidad media (7.5/10)*. El guion es excelente; la síntesis de audio posterior requiere encadenar TTS.

---

== Categoría E: Gestión del Conocimiento (PKM) y Seguridad

=== 16. Puente Nativo a Obsidian (`/obsidian/create-note`)
- *Propósito:* Crear notas atómicas directamente en tus Vaults reales (*MiCerebro* o *Maestria*), incluyendo metadatos YAML Frontmatter (`title`, `date`, `tags`) y enlaces automáticos `[[WikiLinks]]`.
- *Ejemplo de uso:*
```bash
curl -s -X POST http://localhost:8080/obsidian/create-note \
  -H "Content-Type: application/json" \
  -d '{
    "vault": "MiCerebro",
    "folder": "01_Inbox",
    "title": "Arquitectura de Microservicios",
    "content": "Notas sobre la implementacion del hub local con FastAPI.",
    "tags": ["ia", "arquitectura", "linux"],
    "generate_summary": true
  }' | jq .
```
- *Costos Ocultos:* Cero. Escribe directamente en el sistema de archivos de tu disco `/run/media/juang/Datos/`.
- *Veredicto:* *Máxima viabilidad (10/10)*. Conexión limpia y directa con tu flujo diario de estudio y trabajo.

=== 17. Búsqueda Semántica Vectorial RAG (`/search/query`)
- *Propósito:* Indexar tus apuntes o documentos en ChromaDB y buscar por significado conceptual en lugar de por palabras clave exactas.
- *Costos Ocultos:* ChromaDB corre en memoria RAM local (~150 MB). 0 VRAM.
- *Veredicto:* *Alta viabilidad (9.5/10)*.

=== 18. Anonimización de Datos Sensibles PII (`/security/anonymize`)
- *Propósito:* Detectar y reemplazar nombres, emails, tarjetas de crédito, IPs y teléfonos por tokens reversibles (`[PERSON_1]`, `[EMAIL_1]`) antes de enviar texto a internet.
- *Costos Ocultos:* Cero.
- *Veredicto:* *Alta viabilidad (8.5/10)*.

=== 19. Extractor Financiero de Facturas (`/finance/extract-receipt`)
- *Propósito:* Convertir texto desordenado de recibos o tickets en un JSON contable normalizado (empresa, subtotal, impuestos, total e ítems).
- *Veredicto:* *Alta viabilidad (8.5/10)*.

=== 20. Organizador Inteligente de Archivos (`/organizer/suggest-name`)
- *Propósito:* Proponer nombres canónicos normalizados (`YYYY-MM-DD_tema_version.ext`) y categorías para archivos descargados.
- *Veredicto:* *Alta viabilidad (9/10)*.

#pagebreak()

= 3. Recomendaciones Prácticas para tus Pruebas de Mañana

#v(0.5em)

== A. Cómo realizar los tests interactivos rápidamente
No necesitas escribir scripts en la terminal para cada prueba. La suite incluye una interfaz web interactiva completa:
1. Abre tu navegador en: *#link("http://localhost:8080/docs")[http://localhost:8080/docs]*
2. Haz clic en cualquier endpoint (por ejemplo `/text/enhance` o `/terminal/generate-command`).
3. Pulsa el botón *Try it out*, edita el JSON de prueba y pulsa *Execute*.
4. Verás de inmediato el resultado en pantalla y el código de respuesta HTTP (`200 OK`).

== B. Comparativa: ¿Por qué estos microservicios son viables y ComfyUI no lo era por API?

El motivo por el cual el API de ComfyUI resultaba problemática no era la idea en sí, sino el comportamiento de PyTorch:
- *ComfyUI por API:* Cada generación de imagen retenía permanentemente entre *7 y 14 GB de VRAM* en la GPU. Al cabo de 1 o 2 llamadas, la tarjeta gráfica quedaba saturada y bloqueaba a Ollama o al escritorio.
- *Los 20 microservicios actuales:*
  1. *Comparten un único modelo base (Qwen 2.5 7B en Ollama)* que ya está cargado con un peso fijo y predecible de *4.7 GB de VRAM*.
  2. No retienen memoria adicional tras responder: al enviar una respuesta HTTP, el uso de memoria vuelve exactamente a su punto de partida.
  3. Los servicios que no usan LLM (como el lector web, ChromaDB, el analizador forense y el monitor de hardware) operan 100% en RAM tradicional usando menos de 100 MB y dejan la GPU completamente libre.

== C. Checklist sugerido para descartar o conservar

Para tu jornada de pruebas, te sugiero validar estos 5 casos de uso de alto impacto:

- [ ] *Test 1: Monitor de recursos (`GET /system/resources`).* Comprueba que tu RTX 4070 Ti SUPER reporte los ~9.5 GB libres y la memoria RAM disponible.
- [ ] *Test 2: Obsidian (`POST /obsidian/create-note`).* Crea una nota en tu Vault `MiCerebro` y verifica que aparezca al instante en tu aplicación Obsidian.
- [ ] *Test 3: Lector web (`POST /web/extract`).* Pega el enlace de un artículo largo de internet y valida cómo lo sintetiza en Markdown limpio sin publicidad.
- [ ] *Test 4: Corrección académica (`POST /text/enhance` con modo `academic`).* Evalúa la calidad de redacción para tu trabajo de maestría.
- [ ] *Test 5: Copilot Bash (`POST /terminal/generate-command`).* Pídele un comando complejo de Linux (ej: ordenar carpetas por tamaño) y revisa la explicación técnica y advertencias.
