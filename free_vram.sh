#!/usr/bin/env bash
# Script para liberar instantáneamente la VRAM retenida por ComfyUI y PyTorch

echo "🧹 Vaciando caché de VRAM en ComfyUI..."
curl -s -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}' > /dev/null

sleep 1
echo "✅ Memoria liberada. Estado actual de tu GPU:"
nvidia-smi --query-gpu=memory.used,memory.free,memory.total,utilization.gpu --format=csv,noheader
