#!/usr/bin/env python3
"""
Generador Simple de Temperaturas - Versión Línea de Comandos
Genera temperaturas aleatorias para Puntos de Monitoreo específicos.

Uso:
    python simple_temp_seeder.py <nombre_punto>
    
Ejemplo:
    python simple_temp_seeder.py "Biblioteca"
    python simple_temp_seeder.py "Auditorio"
"""

import os
import sys
import django
import time
import random
import requests
import json
from datetime import datetime

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

from quickstart.models import PuntoMonitoreo

def verificar_punto_existe(nombre):
    """Verificar si un Punto de Monitoreo existe en la base de datos."""
    try:
        punto = PuntoMonitoreo.objects.get(nombre=nombre)
        print(f"Punto de Monitoreo encontrado: {nombre}")
        return True
    except PuntoMonitoreo.DoesNotExist:
        print(f"Punto de Monitoreo '{nombre}' no existe")
        return False

def generar_temperaturas(nombre, base_url="http://127.0.0.1:8000"):
    """Genera temperaturas continuas para un punto específico."""
    url = f"{base_url}/api/puntos-monitoreo/reportar_temperatura/"
    
    # Temperatura base aleatoria para este punto
    temp_base = random.uniform(18.0, 25.0)
    intervalo = 5  # Intervalo fijo de 5 segundos
    
    print(f"Iniciando generación de temperaturas para '{nombre}' (base: {temp_base:.1f}°C)")
    print(f"Actualizando cada {intervalo} segundos. Presiona Ctrl+C para detener.")
    print("-" * 60)
    
    try:
        while True:
            # Generar temperatura realista
            variacion = random.uniform(-3.0, 3.0)
            temperatura = temp_base + variacion
            
            # Agregar pequeña tendencia
            tendencia = random.uniform(-0.1, 0.1)
            temp_base += tendencia
            
            # Mantener temperatura en rango razonable
            temperatura = max(10.0, min(35.0, temperatura))
            temp_base = max(15.0, min(30.0, temp_base))
            
            temperatura = round(temperatura, 2)
            
            datos = {
                "nombre_punto": nombre,
                "temperatura": temperatura
            }
            
            try:
                response = requests.post(
                    url, 
                    json=datos, 
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] {nombre}: {temperatura}°C")
                else:
                    print(f"Error al actualizar {nombre}: {response.status_code} - {response.text}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error de red: {e}")
            
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print(f"\nDetenido generación de temperaturas para '{nombre}'")

def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python simple_temp_seeder.py <nombre_punto>")
        print("Ejemplo: python simple_temp_seeder.py 'Biblioteca'")
        sys.exit(1)
    
    nombre = sys.argv[1]
    
    print(f"Objetivo: {nombre}")
    
    # Verificar que el punto existe
    if not verificar_punto_existe(nombre):
        print("El punto de monitoreo no existe. Saliendo.")
        sys.exit(1)
    
    # Iniciar generación de temperaturas
    generar_temperaturas(nombre)

if __name__ == "__main__":
    main()
