# tutorial/quickstart/services/ai_extraction_service.py
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import base64
import os

import openai
from django.conf import settings
import pandas as pd

logger = logging.getLogger(__name__)

class AIExtractionService:
    """Servicio para extraer información de horarios usando IA"""
    
    def __init__(self):
        # Configurar cliente OpenAI desde variables de entorno
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not api_key:
            logger.error("OPENAI_API_KEY no configurada en variables de entorno")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("Cliente OpenAI configurado correctamente")
    
    def procesar_documento(self, documento_horario) -> Dict[str, Any]:
        """Procesa un documento y extrae eventos usando IA"""
        
        if not self.client:
            logger.warning("Cliente OpenAI no configurado, usando modo simulación")
            return self._modo_simulacion(documento_horario)
        
        try:
            # 1. Extraer texto del documento o preparar para Vision API
            contenido = self._extraer_contenido_documento(documento_horario)
            
            if not contenido:
                return {
                    'success': False,
                    'error': 'No se pudo extraer contenido del documento'
                }
            
            logger.info(f"Contenido preparado para IA: {len(str(contenido))} caracteres")
            
            # 2. Usar IA para extraer eventos
            eventos_extraidos = self._extraer_eventos_con_ia(contenido, documento_horario.asignatura)
            
            # 3. Procesar resultados
            eventos_procesados = self._procesar_eventos_extraidos(eventos_extraidos)
            
            logger.info(f"Eventos procesados: {len(eventos_procesados)}")
            
            return {
                'success': True,
                'texto_extraido': str(contenido)[:500] + '...' if len(str(contenido)) > 500 else str(contenido),
                'eventos': eventos_procesados,
                'confianza_promedio': self._calcular_confianza_promedio(eventos_procesados)
            }
            
        except Exception as e:
            logger.error(f"Error procesando documento: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extraer_contenido_documento(self, documento_horario) -> str:
        """Extrae contenido según el tipo de documento"""
        archivo_path = documento_horario.archivo.path
        tipo = documento_horario.tipo_documento.lower()
        archivo_name = documento_horario.archivo.name
        
        try:
            # Para archivos de texto
            if tipo == 'txt':
                return self._leer_archivo_texto(archivo_path)
            
            # Para archivos CSV
            elif tipo == 'csv':
                return self._leer_archivo_csv(archivo_path)
            
            # Para archivos Excel
            elif tipo in ['xlsx', 'excel']:
                return self._leer_archivo_excel(archivo_path)
            
            # Para imágenes - marcar para Vision API
            elif tipo == 'imagen' or self._es_imagen(archivo_name):
                return f"[IMAGEN_PARA_VISION_API:{archivo_path}]"
            
            # Para PDFs (futuro)
            elif archivo_name.lower().endswith('.pdf'):
                return f"[PDF_PARA_PROCESAMIENTO:{archivo_path}]"
            
            # Intentar detectar automáticamente
            else:
                return self._detectar_y_leer_archivo(archivo_path, archivo_name)
                
        except Exception as e:
            logger.error(f"Error extrayendo contenido de {archivo_path}: {str(e)}")
            # Si es imagen, intentar con Vision API de todos modos
            if self._es_imagen(archivo_name):
                return f"[IMAGEN_PARA_VISION_API:{archivo_path}]"
            raise
    
    def _leer_archivo_texto(self, archivo_path: str) -> str:
        """Lee archivo de texto con múltiples encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(archivo_path, 'r', encoding=encoding) as f:
                    contenido = f.read()
                logger.info(f"Archivo de texto leído con encoding {encoding}")
                return contenido
            except UnicodeDecodeError:
                continue
        
        # Si ningún encoding funciona, leer como binario y convertir
        try:
            with open(archivo_path, 'rb') as f:
                contenido_bytes = f.read()
            contenido = contenido_bytes.decode('utf-8', errors='ignore')
            logger.warning("Archivo leído como binario con errores ignorados")
            return contenido
        except Exception as e:
            raise Exception(f"No se pudo leer el archivo de texto: {str(e)}")
    
    def _leer_archivo_csv(self, archivo_path: str) -> str:
        """Lee archivo CSV con múltiples encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(archivo_path, encoding=encoding)
                logger.info(f"CSV leído con encoding {encoding}")
                return df.to_string()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Error leyendo CSV con {encoding}: {e}")
                continue
        
        raise Exception("No se pudo leer el archivo CSV con ningún encoding")
    
    def _leer_archivo_excel(self, archivo_path: str) -> str:
        """Lee archivo Excel"""
        try:
            df = pd.read_excel(archivo_path)
            logger.info("Archivo Excel leído exitosamente")
            return df.to_string()
        except Exception as e:
            raise Exception(f"Error leyendo archivo Excel: {str(e)}")
    
    def _es_imagen(self, archivo_name: str) -> bool:
        """Detecta si el archivo es una imagen"""
        extensiones_imagen = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        return any(archivo_name.lower().endswith(ext) for ext in extensiones_imagen)
    
    def _detectar_y_leer_archivo(self, archivo_path: str, archivo_name: str) -> str:
        """Detecta automáticamente el tipo de archivo"""
        try:
            # Intentar como texto primero
            return self._leer_archivo_texto(archivo_path)
        except:
            # Si falla, verificar si es imagen
            if self._es_imagen(archivo_name):
                return f"[IMAGEN_PARA_VISION_API:{archivo_path}]"
            else:
                raise Exception(f"Tipo de archivo no soportado: {archivo_name}")
    
    def _extraer_eventos_con_ia(self, contenido: str, asignatura) -> List[Dict]:
        """Usa OpenAI para extraer eventos del contenido"""
        
        # Detectar si es imagen para Vision API
        if contenido.startswith("[IMAGEN_PARA_VISION_API:"):
            return self._procesar_imagen_con_vision(contenido, asignatura)
        elif contenido.startswith("[PDF_PARA_PROCESAMIENTO:"):
            return self._procesar_pdf(contenido, asignatura)
        else:
            return self._procesar_texto_con_gpt(contenido, asignatura)
    
    def _procesar_imagen_con_vision(self, contenido_marcador: str, asignatura) -> List[Dict]:
        """Procesa imagen usando GPT-4 Vision"""
        
        # Extraer ruta del archivo
        archivo_path = contenido_marcador.replace("[IMAGEN_PARA_VISION_API:", "").replace("]", "")
        
        try:
            # Convertir imagen a base64
            with open(archivo_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determinar tipo MIME
            if archivo_path.lower().endswith('.png'):
                mime_type = "image/png"
            elif archivo_path.lower().endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            else:
                mime_type = "image/png"
            
            prompt = f"""
            Analiza esta imagen de un horario/calendario académico para la asignatura {asignatura.codigo_completo}.

            BUSCA específicamente:
            - Fechas de exámenes, pruebas, controles, tests, evaluaciones
            - Fechas de entregas de proyectos, tareas, trabajos
            - Fechas de presentaciones, exposiciones, defensas
            - Cualquier evento académico con fecha y hora
            - Información sobre salas, modalidades, instrucciones

            EXTRAE la información exacta que veas en la imagen en formato JSON:
            {{
                "eventos": [
                    {{
                        "titulo": "Nombre exacto del evento",
                        "fecha": "YYYY-MM-DD HH:MM",
                        "descripcion": "Sala, modalidad u otros detalles",
                        "confianza_general": 0.9
                    }}
                ]
            }}

            IMPORTANTE:
            - Si ves fechas pero sin año, asume 2024
            - Si no hay hora específica, usa 14:00 para exámenes, 23:59 para entregas
            - Confianza alta (0.8-1.0) solo si la información es muy clara
            - Si no encuentras eventos claros, responde: {{"eventos": []}}
            
            Responde SOLO con JSON válido, sin texto adicional.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Modelo con capacidades de visión
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            contenido_respuesta = response.choices[0].message.content.strip()
            logger.info(f"Respuesta de GPT-4 Vision: {contenido_respuesta[:200]}...")
            
            return self._parsear_respuesta_json(contenido_respuesta)
            
        except Exception as e:
            logger.error(f"Error procesando imagen con Vision API: {str(e)}")
            return []
    
    def _procesar_texto_con_gpt(self, texto: str, asignatura) -> List[Dict]:
        """Procesa texto usando GPT-4"""
        
        # Limitar texto para evitar límites de tokens
        max_chars = 4000
        texto_limitado = texto[:max_chars]
        if len(texto) > max_chars:
            texto_limitado += "\n... (texto truncado)"
        
        prompt = f"""
        Extrae información de eventos académicos del siguiente texto de la asignatura {asignatura.codigo_completo}:

        {texto_limitado}

        BUSCA específicamente:
        - Fechas de exámenes, pruebas, controles, tests, evaluaciones
        - Fechas de entregas de proyectos, tareas, assignments
        - Fechas de presentaciones, exposiciones, defensas
        - Cualquier evento académico con fecha y hora

        EXTRAE la información en formato JSON:
        {{
            "eventos": [
                {{
                    "titulo": "Nombre del evento",
                    "fecha": "YYYY-MM-DD HH:MM",
                    "descripcion": "Detalles adicionales (sala, modalidad, etc.)",
                    "confianza_general": 0.0-1.0
                }}
            ]
        }}

        IMPORTANTE:
        - Si no hay año, asume 2024
        - Si no hay hora, usa 14:00 para exámenes, 23:59 para entregas
        - Confianza basada en claridad de la información
        - Si no encuentras eventos, responde: {{"eventos": []}}
        
        Responde SOLO con JSON válido.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo eficiente para texto
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto extrayendo fechas de eventos académicos. Responde SOLO con JSON válido."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            contenido_respuesta = response.choices[0].message.content.strip()
            logger.info(f"Respuesta de GPT-4: {contenido_respuesta[:200]}...")
            
            return self._parsear_respuesta_json(contenido_respuesta)
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI para texto: {str(e)}")
            return []
    
    def _procesar_pdf(self, contenido_marcador: str, asignatura) -> List[Dict]:
        """Procesa PDF extrayendo texto real y enviándolo a GPT"""
        archivo_path = contenido_marcador.replace("[PDF_PARA_PROCESAMIENTO:", "").replace("]", "")
        
        try:
            import PyPDF2
            
            texto_completo = ""
            with open(archivo_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"PDF detectado con {len(pdf_reader.pages)} páginas")
                
                for page in pdf_reader.pages:
                    texto_pagina = page.extract_text()
                    if texto_pagina.strip():
                        texto_completo += texto_pagina + "\n"
            
            if not texto_completo.strip():
                logger.warning("PDF no contiene texto extraíble")
                return []
            
            logger.info(f"Texto extraído del PDF: {len(texto_completo)} caracteres")
            
            # Enviar el texto extraído a GPT-4
            return self._procesar_texto_con_gpt(texto_completo, asignatura)
            
        except ImportError:
            logger.error("PyPDF2 no está instalado. Instalar con: pip install PyPDF2")
            return []
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}")
            return []
    
    def _parsear_respuesta_json(self, contenido: str) -> List[Dict]:
        """Parsea la respuesta JSON de OpenAI"""
        try:
            # Limpiar la respuesta
            if contenido.startswith('```json'):
                contenido = contenido.replace('```json', '').replace('```', '').strip()
            elif contenido.startswith('```'):
                contenido = contenido.replace('```', '').strip()
            
            # Parsear JSON
            resultado = json.loads(contenido)
            eventos = resultado.get('eventos', [])
            
            logger.info(f"IA extrajo {len(eventos)} eventos")
            return eventos
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de IA: {str(e)}")
            logger.error(f"Contenido recibido: {contenido}")
            return []
    
    def _procesar_eventos_extraidos(self, eventos_raw: List[Dict]) -> List[Dict]:
        """Procesa y valida eventos extraídos"""
        eventos_procesados = []
        
        for evento in eventos_raw:
            try:
                if 'titulo' not in evento or 'fecha' not in evento:
                    logger.warning(f"Evento sin título o fecha: {evento}")
                    continue
                
                fecha_str = evento.get('fecha', '')
                fecha_parsed = self._parsear_fecha(fecha_str)
                
                if not fecha_parsed:
                    logger.warning(f"No se pudo parsear fecha: {fecha_str}")
                    continue
                
                evento_procesado = {
                    'titulo': str(evento.get('titulo', '')).strip(),
                    'fecha': fecha_parsed,  # Ya es timezone-aware
                    'descripcion': str(evento.get('descripcion', '')).strip(),
                    'confianza_general': float(evento.get('confianza_general', 0.5))
                }
                
                # Validar confianza
                confianza = evento_procesado['confianza_general']
                if confianza < 0 or confianza > 1:
                    evento_procesado['confianza_general'] = 0.5
                
                eventos_procesados.append(evento_procesado)
                logger.info(f"Evento procesado: {evento_procesado['titulo']} - {evento_procesado['fecha']}")
                
            except Exception as e:
                logger.warning(f"Error procesando evento {evento}: {str(e)}")
                continue
        
            return eventos_procesados
    
    def _parsear_fecha(self, fecha_str: str) -> datetime:
        """Intenta parsear una fecha en múltiples formatos con timezone"""
        if not fecha_str:
            return None
            
        fecha_str = fecha_str.strip()
        
        formatos = [
            '%Y-%m-%d %H:%M',      # 2024-12-15 14:30
            '%Y-%m-%d %H:%M:%S',   # 2024-12-15 14:30:00
            '%d/%m/%Y %H:%M',      # 15/12/2024 14:30
            '%d-%m-%Y %H:%M',      # 15-12-2024 14:30
            '%Y-%m-%d',            # 2024-12-15
            '%d/%m/%Y',            # 15/12/2024
            '%d-%m-%Y',            # 15-12-2024
            '%Y-%m-%dT%H:%M:%S',   # ISO format
            '%Y-%m-%dT%H:%M',      # ISO format sin segundos
        ]
        
        for formato in formatos:
            try:
                fecha = datetime.strptime(fecha_str, formato)
                # Si no hay hora, asumir 14:00 (hora típica de exámenes)
                if fecha.hour == 0 and fecha.minute == 0:
                    fecha = fecha.replace(hour=14, minute=0)
                
                # IMPORTANTE: Hacer la fecha timezone-aware
                fecha_con_timezone = timezone.make_aware(fecha, timezone.get_current_timezone())
                return fecha_con_timezone
                
            except ValueError:
                continue
        
        logger.warning(f"No se pudo parsear fecha: {fecha_str}")
        return None
    
    def _calcular_confianza_promedio(self, eventos: List[Dict]) -> float:
        """Calcula confianza promedio de todos los eventos"""
        if not eventos:
            return 0.0
        
        confianzas = [evento.get('confianza_general', 0.0) for evento in eventos]
        return sum(confianzas) / len(confianzas)
    
    def _modo_simulacion(self, documento_horario) -> Dict[str, Any]:
        """Modo simulación cuando no hay API key configurada"""
        logger.info("Ejecutando en modo simulación (sin OpenAI API)")
        
        archivo_name = documento_horario.archivo.name
        eventos_simulados = [
            {
                'titulo': 'Examen Parcial',
                'fecha': datetime(2024, 12, 15, 14, 30),
                'descripcion': f'Extraído de {archivo_name}',
                'confianza_general': 0.85
            },
            {
                'titulo': 'Prueba Final',
                'fecha': datetime(2024, 12, 22, 9, 0),
                'descripcion': 'Evaluación final',
                'confianza_general': 0.90
            }
        ]
        
        return {
            'success': True,
            'texto_extraido': f'Archivo {archivo_name} procesado en modo simulación',
            'eventos': eventos_simulados,
            'confianza_promedio': 0.87
        }