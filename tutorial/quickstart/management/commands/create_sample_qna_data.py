from django.core.management.base import BaseCommand
from quickstart.models import Departamento, Asignatura, Pregunta, Respuesta
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de preguntas y respuestas'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo para el sistema Q&A...')

        # Crear departamentos
        departamentos_data = [
            {'codigo': 'INF', 'nombre': 'Departamento de Informática', 'descripcion': 'Departamento de Ingeniería en Informática'},
            {'codigo': 'FIS', 'nombre': 'Departamento de Física', 'descripcion': 'Departamento de Física'},
            {'codigo': 'MAT', 'nombre': 'Departamento de Matemáticas', 'descripcion': 'Departamento de Matemáticas'},
            {'codigo': 'ELO', 'nombre': 'Departamento de Electrónica', 'descripcion': 'Departamento de Ingeniería Electrónica'},
            {'codigo': 'MEC', 'nombre': 'Departamento de Mecánica', 'descripcion': 'Departamento de Ingeniería Mecánica'},
        ]

        for dept_data in departamentos_data:
            dept, created = Departamento.objects.get_or_create(
                codigo=dept_data['codigo'],
                defaults={
                    'nombre': dept_data['nombre'],
                    'descripcion': dept_data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Departamento creado: {dept}')

        # Crear asignaturas
        asignaturas_data = [
            {'departamento': 'INF', 'numero': '182', 'nombre': 'Programación Orientada a Objetos', 'descripcion': 'Curso de POO con Java'},
            {'departamento': 'INF', 'numero': '134', 'nombre': 'Estructuras de Datos', 'descripcion': 'Algoritmos y estructuras de datos'},
            {'departamento': 'INF', 'numero': '225', 'nombre': 'Base de Datos', 'descripcion': 'Diseño y gestión de bases de datos'},
            {'departamento': 'INF', 'numero': '280', 'nombre': 'Ingeniería de Software', 'descripcion': 'Metodologías de desarrollo de software'},
            {'departamento': 'FIS', 'numero': '120', 'nombre': 'Física I', 'descripcion': 'Mecánica clásica'},
            {'departamento': 'FIS', 'numero': '130', 'nombre': 'Física II', 'descripcion': 'Electromagnetismo'},
            {'departamento': 'MAT', 'numero': '110', 'nombre': 'Cálculo I', 'descripcion': 'Límites, derivadas e integrales'},
            {'departamento': 'MAT', 'numero': '120', 'nombre': 'Cálculo II', 'descripcion': 'Integrales múltiples y series'},
            {'departamento': 'ELO', 'numero': '210', 'nombre': 'Circuitos Eléctricos', 'descripcion': 'Análisis de circuitos eléctricos'},
            {'departamento': 'MEC', 'numero': '150', 'nombre': 'Mecánica de Materiales', 'descripcion': 'Comportamiento mecánico de materiales'},
        ]

        for asig_data in asignaturas_data:
            departamento = Departamento.objects.get(codigo=asig_data['departamento'])
            asig, created = Asignatura.objects.get_or_create(
                departamento=departamento,
                numero=asig_data['numero'],
                defaults={
                    'nombre': asig_data['nombre'],
                    'descripcion': asig_data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Asignatura creada: {asig}')

        # Crear preguntas de ejemplo
        preguntas_data = [
            {
                'asignatura_codigo': 'INF-182',
                'titulo': '¿Cuál es la diferencia entre herencia y composición?',
                'contenido': 'Estoy confundido sobre cuándo usar herencia vs composición en POO. ¿Podrían explicarme las diferencias y cuándo es mejor usar cada una?',
                'nombre_autor': 'EstudianteINF',
                'es_anonima': False
            },
            {
                'asignatura_codigo': 'INF-182',
                'titulo': '¿Cómo implementar el patrón Singleton en Java?',
                'contenido': 'Necesito ayuda para implementar correctamente el patrón Singleton en Java. He visto diferentes versiones y no sé cuál es la mejor.',
                'nombre_autor': None,
                'es_anonima': True
            },
            {
                'asignatura_codigo': 'INF-134',
                'titulo': 'Diferencia entre ArrayList y LinkedList',
                'contenido': '¿Cuáles son las ventajas y desventajas de usar ArrayList vs LinkedList? ¿En qué casos es mejor usar cada una?',
                'nombre_autor': 'María González',
                'es_anonima': False
            },
            {
                'asignatura_codigo': 'FIS-120',
                'titulo': 'Problema con la segunda ley de Newton',
                'contenido': 'Tengo un problema donde un bloque de 5kg está sobre una superficie con fricción μ=0.3. Si aplico una fuerza de 30N, ¿cómo calculo la aceleración?',
                'nombre_autor': None,
                'es_anonima': True
            },
            {
                'asignatura_codigo': 'MAT-110',
                'titulo': '¿Cómo resolver límites indeterminados?',
                'contenido': 'Tengo problemas con límites que dan 0/0 o ∞/∞. ¿Cuáles son las técnicas para resolverlos?',
                'nombre_autor': 'Carlos Estudiante',
                'es_anonima': False
            },
        ]

        for pregunta_data in preguntas_data:
            # Obtener la asignatura
            codigo_parts = pregunta_data['asignatura_codigo'].split('-')
            departamento = Departamento.objects.get(codigo=codigo_parts[0])
            asignatura = Asignatura.objects.get(departamento=departamento, numero=codigo_parts[1])
            
            pregunta, created = Pregunta.objects.get_or_create(
                asignatura=asignatura,
                titulo=pregunta_data['titulo'],
                defaults={
                    'contenido': pregunta_data['contenido'],
                    'nombre_autor': pregunta_data['nombre_autor'],
                    'es_anonima': pregunta_data['es_anonima'],
                    'autor': None  # Por ahora sin usuarios reales
                }
            )
            if created:
                self.stdout.write(f'Pregunta creada: {pregunta.titulo}')

        # Crear algunas respuestas de ejemplo
        respuestas_data = [
            {
                'pregunta_titulo': '¿Cuál es la diferencia entre herencia y composición?',
                'contenido': 'La herencia crea una relación "es-un" mientras que la composición crea una relación "tiene-un". La herencia permite reutilizar código pero crea acoplamiento fuerte. La composición es más flexible pero requiere más código.',
                'nombre_autor': 'ProfesorINF',
                'es_anonima': False,
                'es_respuesta_aceptada': True
            },
            {
                'pregunta_titulo': 'Diferencia entre ArrayList y LinkedList',
                'contenido': 'ArrayList es mejor para acceso aleatorio (get/set) con O(1), pero inserción/eliminación en el medio es O(n). LinkedList es mejor para inserción/eliminación frecuente O(1) pero acceso aleatorio es O(n).',
                'nombre_autor': None,
                'es_anonima': True,
                'es_respuesta_aceptada': False
            },
            {
                'pregunta_titulo': '¿Cómo resolver límites indeterminados?',
                'contenido': 'Las principales técnicas son: 1) Regla de L\'Hôpital para 0/0 y ∞/∞, 2) Factorización y simplificación, 3) Multiplicar por el conjugado, 4) Sustituiciones trigonométricas.',
                'nombre_autor': 'TutorMat',
                'es_anonima': False,
                'es_respuesta_aceptada': True
            },
        ]

        for respuesta_data in respuestas_data:
            try:
                pregunta = Pregunta.objects.get(titulo=respuesta_data['pregunta_titulo'])
                respuesta, created = Respuesta.objects.get_or_create(
                    pregunta=pregunta,
                    contenido=respuesta_data['contenido'],
                    defaults={
                        'nombre_autor': respuesta_data['nombre_autor'],
                        'es_anonima': respuesta_data['es_anonima'],
                        'es_respuesta_aceptada': respuesta_data['es_respuesta_aceptada'],
                        'autor': None  # Por ahora sin usuarios reales
                    }
                )
                if created:
                    self.stdout.write(f'Respuesta creada para: {pregunta.titulo}')
                    
                    # Si es respuesta aceptada, marcar la pregunta como resuelta
                    if respuesta_data['es_respuesta_aceptada']:
                        pregunta.esta_resuelta = True
                        pregunta.save()
            except Pregunta.DoesNotExist:
                self.stdout.write(f'Pregunta no encontrada: {respuesta_data["pregunta_titulo"]}')

        self.stdout.write(
            self.style.SUCCESS('Datos de ejemplo creados exitosamente!')
        )
