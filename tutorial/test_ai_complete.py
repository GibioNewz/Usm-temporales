# test_ai_complete.py
import os
import django
import tempfile
from io import StringIO
import csv

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

from django.contrib.auth.models import User
from quickstart.models import Departamento, Asignatura, DocumentoHorario
from quickstart.services.ai_extraction_service import AIExtractionService

def crear_datos_prueba():
    """Crear datos básicos para las pruebas"""
    print("🔧 Creando datos de prueba...")
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'test@student.com',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Crear departamento
    dept, created = Departamento.objects.get_or_create(
        codigo='INF',
        defaults={
            'nombre': 'Departamento de Informática',
            'descripcion': 'Departamento de Ingeniería en Informática'
        }
    )
    
    # Crear asignatura
    asignatura, created = Asignatura.objects.get_or_create(
        departamento=dept,
        numero='182',
        defaults={
            'nombre': 'Programación Orientada a Objetos',
            'descripcion': 'Curso de POO con Java'
        }
    )
    
    print(f"✅ Usuario: {user.username}")
    print(f"✅ Asignatura: {asignatura.codigo_completo}")
    
    return user, asignatura

def crear_archivo_prueba():
    """Crear un archivo CSV de prueba con horarios"""
    content = """Evento,Fecha,Hora,Sala,Descripción
Control 1,2024-12-15,14:30,A-101,Primer control de programación
Prueba Global,2024-12-20,09:00,B-205,Examen global del semestre
Entrega Proyecto,2024-12-18,23:59,Online,Entrega final del proyecto POO
Control 2,2025-01-10,15:45,A-102,Segundo control después de vacaciones
"""
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    print(f"📄 Archivo de prueba creado: {temp_file.name}")
    return temp_file.name

def probar_extraccion_ia():
    """Probar todo el flujo de extracción con IA"""
    print("\n🧪 PROBANDO SISTEMA COMPLETO DE EXTRACCIÓN")
    print("=" * 50)
    
    # 1. Crear datos de prueba
    user, asignatura = crear_datos_prueba()
    
    # 2. Crear archivo de prueba
    archivo_path = crear_archivo_prueba()
    
    try:
        # 3. Crear documento horario
        print("\n📤 Subiendo documento...")
        with open(archivo_path, 'rb') as f:
            documento = DocumentoHorario.objects.create(
                archivo=f.name,
                tipo_documento='csv',
                asignatura=asignatura,
                subido_por=user
            )
        
        print(f"✅ Documento creado: ID {documento.id}")
        
        # 4. Probar servicio de IA
        print("\n🤖 Probando extracción con IA...")
        ai_service = AIExtractionService()
        
        if not ai_service.client:
            print("⚠️ No se puede probar IA - API key no configurada")
            print("👉 Para probar completamente, configura tu OpenAI API key en .env")
            return documento
        
        # 5. Procesar con IA
        resultado = ai_service.procesar_documento(documento)
        
        print(f"📊 Resultado del procesamiento:")
        print(f"  - Éxito: {resultado['success']}")
        
        if resultado['success']:
            print(f"  - Texto extraído: {len(resultado['texto_extraido'])} caracteres")
            print(f"  - Eventos detectados: {len(resultado['eventos'])}")
            print(f"  - Confianza promedio: {resultado['confianza_promedio']:.2f}")
            
            # Mostrar eventos detectados
            print("\n📅 Eventos detectados:")
            for i, evento in enumerate(resultado['eventos'], 1):
                print(f"  {i}. {evento['titulo']}")
                print(f"     Fecha: {evento['fecha']}")
                print(f"     Descripción: {evento['descripcion']}")
                print(f"     Confianza: {evento['confianza_general']:.2f}")
                print()
        else:
            print(f"  - Error: {resultado['error']}")
        
        return documento
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        return None
    
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(archivo_path)
        except:
            pass

def probar_api_endpoints():
    """Probar que los endpoints de API están disponibles"""
    print("\n🌐 PROBANDO ENDPOINTS DE API")
    print("=" * 30)
    
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    endpoints = [
        '/api/documentos-horario/',
        '/api/eventos-extraidos/',
        '/api/documentos-horario/estadisticas/',
    ]
    
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            status_icon = "✅" if response.status_code in [200, 401] else "❌"
            print(f"{status_icon} {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

def mostrar_instrucciones():
    """Mostrar instrucciones para usar el sistema"""
    print("\n📋 INSTRUCCIONES PARA USAR EL SISTEMA")
    print("=" * 40)
    print("1. Configura tu OpenAI API key en el archivo .env:")
    print("   OPENAI_API_KEY=tu-api-key-real")
    print()
    print("2. Inicia el servidor de desarrollo:")
    print("   python manage.py runserver")
    print()
    print("3. Ve a la API navegable:")
    print("   http://localhost:8000/api/")
    print()
    print("4. Endpoints disponibles:")
    print("   - http://localhost:8000/api/documentos-horario/")
    print("   - http://localhost:8000/api/eventos-extraidos/")
    print("   - http://localhost:8000/api/documentos-horario/estadisticas/")
    print()
    print("5. Para subir un documento vía API:")
    print("   POST /api/documentos-horario/")
    print("   Form-data: archivo (file), asignatura (int)")
    print()
    print("6. El sistema procesará automáticamente con IA y extraerá eventos")

if __name__ == "__main__":
    try:
        # Ejecutar pruebas
        documento = probar_extraccion_ia()
        probar_api_endpoints()
        
        # Mostrar estadísticas
        if documento:
            total_docs = DocumentoHorario.objects.count()
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   Total documentos: {total_docs}")
            print(f"   Último documento: {documento.archivo.name if documento.archivo else 'N/A'}")
        
        # Mostrar instrucciones
        mostrar_instrucciones()
        
        print("\n🎉 ¡Sistema listo para usar!")
        
    except KeyboardInterrupt:
        print("\n👋 Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        print("🔧 Verifica que todas las migraciones estén aplicadas:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")