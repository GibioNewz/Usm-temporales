# tutorial/test_setup.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

from quickstart.services.ai_extraction_service import AIExtractionService

def test_setup():
    print("🧪 Probando configuración...")
    
    service = AIExtractionService()
    
    if service.client is None:
        print("❌ API key no configurada")
        print("👉 Edita tutorial/tutorial/settings.py y cambia 'tu-api-key-aqui'")
    else:
        print("✅ ¡Todo configurado correctamente!")
        print("🎯 Listo para el siguiente paso")

if __name__ == "__main__":
    test_setup()