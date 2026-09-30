#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"

# Añadir dinámicamente librerías de NVIDIA instaladas en el virtualenv
NVIDIA_LIBS=$(find "$DIR/.venv/lib" -type d -path "*/nvidia/*/lib" 2>/dev/null | tr '\n' ':')
export LD_LIBRARY_PATH="$NVIDIA_LIBS$LD_LIBRARY_PATH"

echo "🚀 Iniciando AI Gateway en http://localhost:8080"
echo "📖 Swagger UI interactivo disponible en http://localhost:8080/docs"

exec "$DIR/.venv/bin/uvicorn" main:app --app-dir "$DIR" --host 0.0.0.0 --port 8080
