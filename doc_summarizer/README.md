# Resumidor y Organizador Automático de Documentos (APA 7)

Servicio en segundo plano que detecta documentos colocados en tu carpeta de originales (`.pdf`, `.docx`, `.txt`, etc.), sintetiza un resumen académico con normas **APA 7.ª edición** mediante un modelo local en **Ollama**, compila un PDF formal con **Typst** y guarda los resúmenes organizados en carpetas `md/` y `pdf/`.

---

## 📁 Estructura de Organización

Los archivos se gestionan en `~/Documentos/Biblioteca_IA/`:

- `Originales/`: Carpeta monitoreada. Coloca aquí los documentos que desees resumir (los archivos se mantienen aquí sin moverse).
- `md/`: Contiene los resúmenes en Markdown (`[nombre]_resumen_APA7.md`) con Frontmatter YAML estructurado para lectura rápida o indexación.
- `pdf/`: Contiene los resúmenes formales en PDF (`[nombre]_resumen_APA7.pdf`) compilados según directrices APA 7 (Portada, resumen, objetivos, metodología, hallazgos, conclusiones, palabras clave y referencias con sangría francesa).

---

## ⚙️ Configuración (`config.yaml`)

Puedes modificar el comportamiento en [config.yaml](config.yaml):
- `watch_folder`: Directorio monitoreado (`~/Documentos/Biblioteca_IA/Originales`).
- `storage_base_dir`: Directorio base (`~/Documentos/Biblioteca_IA`).
- `subdirs`: Carpetas `originals`, `md` y `pdf`.
- `ollama.model`: Modelo local utilizado (`qwen2.5:7b`).
- `settings.organize_originals`: Por defecto `false` (no mueve el original de la carpeta donde lo colocas).
- `settings.desktop_notifications`: Notificaciones nativas en el escritorio con `notify-send`.

---

## 🛠️ Comandos Disponibles

Desde el directorio del proyecto `doc_summarizer/`:

```bash
# Diagnóstico de Ollama y Typst
.venv/bin/python main.py check

# Procesar manualmente un archivo específico
.venv/bin/python main.py process /ruta/al/documento.pdf

# Procesar todos los documentos pendientes que estén en Originales
.venv/bin/python main.py process-pending
```

---

## 🔄 Control del Servicio en Segundo Plano (Systemd)

El servicio ya se encuentra instalado y corriendo en tu usuario:

```bash
# Ver estado del servicio
systemctl --user status doc-summarizer.service

# Ver logs en vivo
journalctl --user -u doc-summarizer.service -f

# Detener o reiniciar el servicio
systemctl --user stop doc-summarizer.service
systemctl --user restart doc-summarizer.service
```
