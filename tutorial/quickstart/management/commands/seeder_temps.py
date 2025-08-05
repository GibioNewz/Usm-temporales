from django.core.management.base import BaseCommand
from quickstart.models import PuntoMonitoreo
import random
import time
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Simular sensores IoT enviando datos de temperatura a través de la API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Intervalo de actualización en segundos (por defecto: 15)'
        )
        parser.add_argument(
            '--base-url',
            type=str,
            default='http://localhost:8000',
            help='URL base para llamadas a la API (por defecto: http://localhost:8000)'
        )

    def handle(self, *args, **options):
        intervalo = options['interval']
        url_base = options['base_url'].rstrip('/')

        self.stdout.write(
            self.style.SUCCESS(
                f'Iniciando simulación de sensores cada {intervalo} segundos...\n'
                f'URL base de la API: {url_base}\n'
                f'Presiona Ctrl+C para detener'
            )
        )

        try:
            while True:
                self.simular_sensores(url_base)
                time.sleep(intervalo)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nSimulación de sensores detenida.'))

    def simular_sensores(self, url_base):
        """Simular el envío de datos desde sensores IoT"""
        puntos = PuntoMonitoreo.objects.all()
        
        if not puntos.exists():
            self.stdout.write(self.style.WARNING('No se encontraron puntos de monitoreo. Ejecuta seed_data primero.'))
            return

        for punto in puntos:
            # Generar lectura realista de temperatura
            temp_base = punto.temperatura_actual or 20.0
            # Simular ruido del sensor y cambios ambientales
            temperatura = round(temp_base + random.uniform(-1.5, 1.5), 1)
            
            # Simular llamada a la API del endpoint reportar_temperatura
            try:
                response = requests.post(
                    f'{url_base}/puntos-monitoreo/reportar_temperatura/',
                    json={
                        'nombre_punto': punto.nombre,
                        'temperatura': temperatura
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.stdout.write(
                        f'✓ Sensor {punto.nombre}: {temperatura}°C reportado exitosamente'
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Sensor {punto.nombre}: Error de API {response.status_code}'
                        )
                    )
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Sensor {punto.nombre}: Error de conexión - {e}'
                    )
                )

        self.stdout.write(f'Ciclo de simulación de sensores completado\n')