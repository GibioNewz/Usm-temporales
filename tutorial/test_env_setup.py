# test_env_setup.py (junto a manage.py)
import os
import sys
import django

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

try:
    from decouple import config
    print("✅ python-decouple importado correctamente")
except ImportError:
    print("❌ Falta instalar python-decouple")
    print("👉 Ejecuta: pip install python-decouple")
    sys.exit(1)

def test_configuration():
    print("\n🧪 Validando configuración con variables de entorno...")
    print("=" * 50)
    
    # Verificar variables de entorno
    try:
        openai_key = config('OPENAI_API_KEY', default='')
        debug = config('DEBUG', default=False, cast=bool)
        
        print(f"📁 Archivo .env detectado: {os.path.exists('.env')}")
        print(f"🔑 OpenAI API Key configurada: {'✅ Sí' if openai_key else '❌ No'}")
        print(f"🐛 Debug mode: {'✅ Activado' if debug else '⚠️ Desactivado'}")
        
        # Probar importación del servicio
        try:
            from quickstart.services.ai_extraction_service import AIExtractionService
            print("✅ Servicio de IA importado correctamente")
            
            service = AIExtractionService()
            
            if service.client is None:
                print("\n❌ PROBLEMA: Cliente OpenAI no configurado")
                print("👉 Solución:")
                print("   1. Crea el archivo .env en esta carpeta")
                print("   2. Añade: OPENAI_API_KEY=tu-api-key-real")
                print("   3. Obtén tu API key en: https://platform.openai.com/account/api-keys")
                return False
            else:
                print("\n✅ ¡Configuración perfecta!")
                print("🎯 Variables de entorno funcionando correctamente")
                print("🚀 Listo para procesar documentos de horarios")
                return True
                
        except ImportError as e:
            print(f"❌ Error importando servicio de IA: {e}")
            print("👉 Verifica que creaste la carpeta quickstart/services/")
            return False
            
    except Exception as e:
        print(f"❌ Error con configuración: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_configuration()
        if not success:
            print("\n🔧 Necesitas completar la configuración antes de continuar")
        else:
            print("\n📋 SIGUIENTE PASO: Crear las vistas de API")
    except KeyboardInterrupt:
        print("\n👋 Prueba cancelada")