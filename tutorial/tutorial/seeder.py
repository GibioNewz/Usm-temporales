from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quickstart.models import Departamento, Asignatura, Pregunta, Respuesta, PuntoMonitoreo, Event
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Llenar la base de datos con datos iniciales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de datos...'))

        # Crear usuarios
        self.crear_usuarios()
        
        # Crear departamentos
        self.crear_departamentos()
        
        # Crear asignaturas
        self.crear_asignaturas()
        
        # Crear puntos de monitoreo
        self.crear_puntos_monitoreo()
        
        # Crear preguntas y respuestas
        self.crear_preguntas_y_respuestas()
        
        # Crear eventos
        self.crear_eventos()

        self.stdout.write(self.style.SUCCESS('¡Carga de datos completada exitosamente!'))

    def crear_usuarios(self):
        """Crear usuarios de ejemplo para el sistema"""
        usuarios_data = [
            {'username': 'profesor1', 'email': 'profesor1@univ.cl', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'profesor2', 'email': 'profesor2@univ.cl', 'first_name': 'María', 'last_name': 'González'},
            {'username': 'estudiante1', 'email': 'estudiante1@univ.cl', 'first_name': 'Carlos', 'last_name': 'López'},
            {'username': 'estudiante2', 'email': 'estudiante2@univ.cl', 'first_name': 'Ana', 'last_name': 'Martínez'},
            {'username': 'admin', 'email': 'admin@univ.cl', 'first_name': 'Admin', 'last_name': 'Sistema'},
        ]

        for usuario_data in usuarios_data:
            usuario, creado = User.objects.get_or_create(
                username=usuario_data['username'],
                defaults={
                    'email': usuario_data['email'],
                    'first_name': usuario_data['first_name'],
                    'last_name': usuario_data['last_name'],
                }
            )
            if creado:
                usuario.set_password('password123')
                usuario.save()
                self.stdout.write(f'Usuario creado: {usuario.username}')

    def crear_departamentos(self):
        """Crear departamentos académicos básicos"""
        departamentos_data = [
            {'codigo': 'INF', 'nombre': 'Departamento de Informática', 'descripcion': 'Departamento de Ciencias de la Computación e Informática'},
            {'codigo': 'FIS', 'nombre': 'Departamento de Física', 'descripcion': 'Departamento de Física y Astronomía'},
            {'codigo': 'MAT', 'nombre': 'Departamento de Matemáticas', 'descripcion': 'Departamento de Matemáticas y Estadística'},
            {'codigo': 'IND', 'nombre': 'Departamento de Ingeniería Industrial', 'descripcion': 'Departamento de Ingeniería Industrial y de Sistemas'},
            {'codigo': 'CIV', 'nombre': 'Departamento de Ingeniería Civil', 'descripcion': 'Departamento de Ingeniería Civil y Ambiental'},
        ]

        for dept_data in departamentos_data:
            dept, creado = Departamento.objects.get_or_create(
                codigo=dept_data['codigo'],
                defaults={
                    'nombre': dept_data['nombre'],
                    'descripcion': dept_data['descripcion'],
                }
            )
            if creado:
                self.stdout.write(f'Departamento creado: {dept.codigo} - {dept.nombre}')

    def crear_asignaturas(self):
        """Crear asignaturas de ejemplo para cada departamento"""
        asignaturas_data = [
            # Asignaturas de INF
            {'dept_codigo': 'INF', 'numero': '101', 'nombre': 'Introducción a la Programación', 'descripcion': 'Fundamentos de programación'},
            {'dept_codigo': 'INF', 'numero': '182', 'nombre': 'Estructuras de Datos', 'descripcion': 'Algoritmos y estructuras de datos'},
            {'dept_codigo': 'INF', 'numero': '280', 'nombre': 'Base de Datos', 'descripcion': 'Diseño y administración de bases de datos'},
            {'dept_codigo': 'INF', 'numero': '381', 'nombre': 'Ingeniería de Software', 'descripcion': 'Metodologías de desarrollo de software'},
            
            # Asignaturas de FIS
            {'dept_codigo': 'FIS', 'numero': '120', 'nombre': 'Física General I', 'descripcion': 'Mecánica clásica'},
            {'dept_codigo': 'FIS', 'numero': '220', 'nombre': 'Física General II', 'descripcion': 'Electricidad y magnetismo'},
            
            # Asignaturas de MAT
            {'dept_codigo': 'MAT', 'numero': '101', 'nombre': 'Cálculo I', 'descripcion': 'Límites, derivadas e integrales'},
            {'dept_codigo': 'MAT', 'numero': '201', 'nombre': 'Cálculo II', 'descripcion': 'Integrales múltiples y series'},
            
            # Asignaturas de IND
            {'dept_codigo': 'IND', 'numero': '101', 'nombre': 'Introducción a la Ingeniería Industrial', 'descripcion': 'Fundamentos de la ingeniería industrial'},
            {'dept_codigo': 'IND', 'numero': '250', 'nombre': 'Investigación de Operaciones', 'descripcion': 'Optimización y modelos matemáticos'},
        ]

        for asignatura_data in asignaturas_data:
            dept = Departamento.objects.get(codigo=asignatura_data['dept_codigo'])
            asignatura, creado = Asignatura.objects.get_or_create(
                departamento=dept,
                numero=asignatura_data['numero'],
                defaults={
                    'nombre': asignatura_data['nombre'],
                    'descripcion': asignatura_data['descripcion'],
                }
            )
            if creado:
                self.stdout.write(f'Asignatura creada: {asignatura.get_codigo_completo()} - {asignatura.nombre}')

    def crear_puntos_monitoreo(self):
        """Crear puntos de monitoreo con temperaturas iniciales"""
        puntos_data = [
            {'nombre': 'Biblioteca Central', 'temperatura': round(random.uniform(18.0, 25.0), 1)},
            {'nombre': 'Auditorio Principal', 'temperatura': round(random.uniform(19.0, 26.0), 1)},
            {'nombre': 'Laboratorio de Informática', 'temperatura': round(random.uniform(20.0, 28.0), 1)},
            {'nombre': 'Cafetería', 'temperatura': round(random.uniform(22.0, 30.0), 1)},
            {'nombre': 'Sala de Estudios A', 'temperatura': round(random.uniform(18.5, 24.5), 1)},
            {'nombre': 'Sala de Estudios B', 'temperatura': round(random.uniform(19.5, 25.5), 1)},
            {'nombre': 'Laboratorio de Física', 'temperatura': round(random.uniform(17.0, 23.0), 1)},
            {'nombre': 'Aula Magna', 'temperatura': round(random.uniform(20.5, 27.0), 1)},
        ]

        for punto_data in puntos_data:
            punto, creado = PuntoMonitoreo.objects.get_or_create(
                nombre=punto_data['nombre'],
                defaults={'temperatura_actual': punto_data['temperatura']}
            )
            if creado:
                self.stdout.write(f'Punto de monitoreo creado: {punto.nombre} - {punto.temperatura_actual}°C')

    def crear_preguntas_y_respuestas(self):
        """Crear preguntas y respuestas de ejemplo para el sistema Q&A"""
        usuarios = User.objects.all()
        asignaturas = Asignatura.objects.all()

        preguntas_data = [
            {
                'asignatura': 'INF-101',
                'titulo': '¿Cómo implementar un algoritmo de búsqueda binaria?',
                'contenido': 'Tengo dudas sobre la implementación correcta del algoritmo de búsqueda binaria en Python. ¿Podrían ayudarme con la sintaxis?',
                'es_anonima': False,
                'autor': 'estudiante1'
            },
            {
                'asignatura': 'INF-182',
                'titulo': 'Diferencia entre Stack y Queue',
                'contenido': '¿Cuál es la principal diferencia entre estas estructuras de datos y cuándo usar cada una? Necesito entender mejor sus casos de uso.',
                'es_anonima': True,
                'nombre_autor': 'EstudianteAnonimo1'
            },
            {
                'asignatura': 'FIS-120',
                'titulo': 'Problemas con cinemática',
                'contenido': 'No entiendo cómo resolver problemas de movimiento uniformemente acelerado. ¿Alguien me puede explicar paso a paso?',
                'es_anonima': False,
                'autor': 'estudiante2'
            },
            {
                'asignatura': 'MAT-101',
                'titulo': 'Límites infinitos',
                'contenido': '¿Cómo se resuelven los límites cuando x tiende a infinito? Me confunden las indeterminaciones.',
                'es_anonima': True,
                'nombre_autor': 'MathStudent'
            },
            {
                'asignatura': 'INF-280',
                'titulo': 'Normalización de bases de datos',
                'contenido': 'Necesito ayuda para entender las formas normales en el diseño de bases de datos. ¿Cuándo aplicar cada una?',
                'es_anonima': False,
                'autor': 'estudiante1'
            }
        ]

        for pregunta_data in preguntas_data:
            try:
                asignatura = Asignatura.objects.get(
                    departamento__codigo=pregunta_data['asignatura'].split('-')[0],
                    numero=pregunta_data['asignatura'].split('-')[1]
                )
                
                pregunta_defaults = {
                    'titulo': pregunta_data['titulo'],
                    'contenido': pregunta_data['contenido'],
                    'es_anonima': pregunta_data['es_anonima'],
                }
                
                if pregunta_data['es_anonima']:
                    pregunta_defaults['nombre_autor'] = pregunta_data['nombre_autor']
                else:
                    pregunta_defaults['autor'] = User.objects.get(username=pregunta_data['autor'])

                pregunta, creado = Pregunta.objects.get_or_create(
                    asignatura=asignatura,
                    titulo=pregunta_data['titulo'],
                    defaults=pregunta_defaults
                )
                
                if creado:
                    self.stdout.write(f'Pregunta creada: {pregunta.titulo}')
                    
                    # Crear algunas respuestas para cada pregunta
                    if not pregunta_data['es_anonima']:
                        # Respuesta autenticada
                        Respuesta.objects.create(
                            pregunta=pregunta,
                            autor=random.choice(usuarios),
                            contenido=f'Esta es una respuesta detallada para la pregunta sobre {pregunta.titulo.lower()}. Te recomiendo revisar la documentación oficial y practicar con ejemplos similares.',
                            es_anonima=False
                        )
                        
                    # Respuesta anónima
                    Respuesta.objects.create(
                        pregunta=pregunta,
                        contenido=f'Respuesta de ayudante: Para resolver este tipo de problemas, te sugiero seguir estos pasos metodológicos y consultar fuentes adicionales.',
                        es_anonima=True,
                        nombre_autor=f'Ayudante{random.randint(1, 100)}'
                    )
                    
            except Exception as e:
                self.stdout.write(f'Error creando pregunta: {e}')

    def crear_eventos(self):
        """Crear eventos de ejemplo para el calendario académico"""
        usuarios = User.objects.all()
        eventos_data = [
            {
                'title': 'Seminario de Inteligencia Artificial',
                'description': 'Conferencia sobre las últimas tendencias en IA y machine learning aplicado a la industria.',
                'date': timezone.now() + timezone.timedelta(days=7)
            },
            {
                'title': 'Workshop de Desarrollo Web',
                'description': 'Taller práctico sobre desarrollo frontend y backend con tecnologías modernas como React y Django.',
                'date': timezone.now() + timezone.timedelta(days=14)
            },
            {
                'title': 'Feria de Proyectos Estudiantiles',
                'description': 'Exposición de proyectos finales desarrollados por estudiantes de ingeniería de todos los departamentos.',
                'date': timezone.now() + timezone.timedelta(days=21)
            },
            {
                'title': 'Conferencia de Física Cuántica',
                'description': 'Charla magistral sobre los avances en física cuántica aplicada y computación cuántica.',
                'date': timezone.now() + timezone.timedelta(days=10)
            },
            {
                'title': 'Hackathon Universitario',
                'description': 'Competencia de programación de 24 horas para resolver problemas reales de la industria.',
                'date': timezone.now() + timezone.timedelta(days=30)
            }
        ]

        for evento_data in eventos_data:
            evento, creado = Event.objects.get_or_create(
                title=evento_data['title'],
                defaults={
                    'description': evento_data['description'],
                    'date': evento_data['date'],
                    'created_by': random.choice(usuarios)
                }
            )
            if creado:
                self.stdout.write(f'Evento creado: {evento.title}')