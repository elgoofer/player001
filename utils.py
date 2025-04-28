# utils.py

def formatear_tiempo(segundos):
    # Función para convertir segundos a formato "minutos:segundos"
    minutos = int(segundos // 60)
    seg = int(segundos % 60)
    return f"{minutos}:{seg:02d}"
