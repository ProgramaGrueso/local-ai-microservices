import subprocess
import shutil
import httpx
import psutil
from fastapi import APIRouter, HTTPException
from core.config import settings

router = APIRouter(prefix="/system", tags=["💻 Monitoreo de Hardware (RAM & VRAM)"])

def get_nvidia_gpu_info():
    """Obtiene métricas de VRAM y GPU usando nvidia-smi de forma no bloqueante."""
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return {"error": "nvidia-smi no está disponible en el sistema"}
    try:
        cmd = [
            nvidia_smi,
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
            "--format=csv,noheader,nounits"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        line = res.stdout.strip()
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 6:
            name, total_mb, used_mb, free_mb, util_pct, temp_c = parts
            total_mib = float(total_mb)
            used_mib = float(used_mb)
            free_mib = float(free_mb)
            return {
                "gpu_name": name,
                "vram_total_gb": round(total_mib / 1024, 2),
                "vram_used_gb": round(used_mib / 1024, 2),
                "vram_free_gb": round(free_mib / 1024, 2),
                "vram_used_percentage": round((used_mib / total_mib) * 100, 1),
                "gpu_utilization_percentage": int(util_pct),
                "temperature_celsius": int(temp_c)
            }
    except Exception as e:
        return {"error": f"Fallo al consultar nvidia-smi: {str(e)}"}
    return {"error": "Respuesta inesperada de nvidia-smi"}

@router.get("/resources")
async def get_system_resources():
    """
    Devuelve el uso en tiempo real de RAM del sistema (psutil) y VRAM de la GPU NVIDIA (RTX 4070 Ti SUPER).
    """
    # RAM del sistema
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    ram_data = {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "percentage_used": mem.percent
    }
    
    swap_data = {
        "total_gb": round(swap.total / (1024 ** 3), 2),
        "used_gb": round(swap.used / (1024 ** 3), 2),
        "free_gb": round(swap.free / (1024 ** 3), 2),
        "percentage_used": swap.percent
    }

    # GPU VRAM
    gpu_data = get_nvidia_gpu_info()

    return {
        "status": "healthy",
        "system_ram": ram_data,
        "system_swap": swap_data,
        "gpu_nvidia": gpu_data
    }

@router.post("/free-vram")
async def free_all_vram():
    """
    Libera la memoria de video (VRAM) descargando modelos en ComfyUI.
    """
    comfy_res = "No contactado"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{settings.COMFYUI_HOST}/free",
                json={"unload_models": True, "free_memory": True}
            )
            comfy_res = res.text
    except Exception as e:
        comfy_res = f"ComfyUI no respondió: {e}"

    # Retornar estado actualizado tras liberar
    gpu_after = get_nvidia_gpu_info()
    return {
        "message": "Comando de liberación de memoria VRAM ejecutado.",
        "comfyui_response": comfy_res,
        "gpu_vram_actual": gpu_after
    }
