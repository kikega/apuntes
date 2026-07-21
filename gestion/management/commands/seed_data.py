from django.core.management.base import BaseCommand
from django.utils.text import slugify
from gestion.models import Categoria, Familia, Tema, Apunte
from typing import Any


class Command(BaseCommand):
    help = "Puebla la base de datos con categorías, temas y apuntes técnicos de demostración."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Limpiando datos existentes...")
        Apunte.objects.all().delete()
        Tema.objects.all().delete()
        Familia.objects.all().delete()
        Categoria.objects.all().delete()

        self.stdout.write("Creando categorías principales...")
        
        # Categorías
        cat_prog = Categoria.objects.create(
            nombre="Programación",
            descripcion="Apuntes sobre lenguajes, frameworks y arquitectura de software backend/frontend."
        )
        cat_db = Categoria.objects.create(
            nombre="Bases de Datos",
            descripcion="Administración, modelado, consultas y optimización en SQL y NoSQL."
        )
        
        # Familias
        self.stdout.write("Creando familias...")
        fam_back = Familia.objects.create(
            nombre="Backend",
            categoria=cat_prog,
            descripcion="Lógica del lado del servidor, APIs y servicios."
        )
        fam_front = Familia.objects.create(
            nombre="Frontend",
            categoria=cat_prog,
            descripcion="Interfaces de usuario, maquetación, estilos y reactividad."
        )
        fam_rel = Familia.objects.create(
            nombre="Relacionales",
            categoria=cat_db,
            descripcion="Sistemas de gestión de bases de datos relacionales tradicionales."
        )
        fam_nosql = Familia.objects.create(
            nombre="NoSQL",
            categoria=cat_db,
            descripcion="Bases de datos no relacionales, clave-valor, documentales y grafos."
        )
        
        # Temas
        self.stdout.write("Creando temas...")
        tema_django = Tema.objects.create(
            nombre="Django Framework",
            familia=fam_back,
            descripcion="Framework robusto y seguro para desarrollo rápido en Python."
        )
        tema_fastapi = Tema.objects.create(
            nombre="FastAPI",
            familia=fam_back,
            descripcion="API Framework de alto rendimiento basado en Python Type Hints y Pydantic."
        )
        tema_vue = Tema.objects.create(
            nombre="Vue.js",
            familia=fam_front,
            descripcion="Framework progresivo de Javascript para interfaces interactivas."
        )
        tema_postgres = Tema.objects.create(
            nombre="PostgreSQL",
            familia=fam_rel,
            descripcion="Motor relacional open-source sumamente avanzado y extensible."
        )
        tema_redis = Tema.objects.create(
            nombre="Redis",
            familia=fam_nosql,
            descripcion="Almacén de estructuras de datos en memoria utilizado como DB y caché."
        )

        # Apuntes
        self.stdout.write("Creando apuntes y guías de estudio...")
        
        # 1. Django (Markdown)
        Apunte.objects.create(
            tema=tema_django,
            titulo="Introducción a Django y el patrón MVT",
            contenido="""# Introducción a Django y el patrón MVT

Django es un framework web de alto nivel escrito en Python que fomenta un desarrollo rápido y un diseño limpio y pragmático. Sigue el patrón de diseño **MVT (Model-View-Template)**.

## ¿Qué significa MVT?

1. **Modelo (Model):** Define la estructura de datos. Django mapea automáticamente tus clases en archivos `models.py` a tablas SQL en la base de datos usando su potente ORM.
2. **Vista (View):** Contiene la lógica de negocio y procesamiento de peticiones. Recibe una petición HTTP y devuelve una respuesta HTTP (o renderiza un Template).
3. **Plantilla (Template):** La interfaz que el usuario final visualiza (HTML dinámico usando el motor de plantillas de Django).

## Ejemplo de Configuración en Django

Configurar una base de datos PostgreSQL en `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mi_base_de_datos',
        'USER': 'kike',
        'PASSWORD': 'password_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> **Consejo de Seguridad:** Nunca expongas credenciales en texto plano. Utiliza variables de entorno (`.env`) con bibliotecas como `django-environ`.
""",
            formato="MD",
            estado="COMPLETADO"
        )
        
        # 2. Django - CBV vs FBV (Markdown)
        Apunte.objects.create(
            tema=tema_django,
            titulo="Vistas Basadas en Clases (CBV) frente a Funciones (FBV)",
            contenido="""# Vistas Basadas en Clases (CBV) frente a Funciones (FBV)

En Django, existen dos enfoques principales para definir la lógica de tus endpoints:

## 1. Vistas basadas en funciones (FBV)
Son simples funciones que reciben un `request` y retornan un `response`. Son ideales para lógica simple y directa.

```python
from django.shortcuts import render
from django.http import HttpResponse

def saludo_view(request):
    if request.method == 'GET':
        return HttpResponse("¡Hola Mundo!")
```

## 2. Vistas basadas en clases (CBV)
Utilizan programación orientada a objetos para estructurar y reutilizar código. Django provee clases genéricas como `ListView`, `DetailView` y `CreateView` para resolver casos de uso comunes.

```python
from django.views.generic import ListView
from .models import Apunte

class ApunteListView(ListView):
    model = Apunte
    template_name = "gestion/dashboard.html"
    context_object_name = "apuntes"
    
    def get_queryset(self):
        # Optimización con select_related
        return Apunte.objects.select_related('tema')
```

### Ventajas de las CBVs:
* **DRY (Don't Repeat Yourself):** Reutilización de código a través de herencia y Mixins.
* **Organización:** Separación de métodos HTTP (`get`, `post`, `put`, `delete`) de forma natural en métodos de clase.
""",
            formato="MD",
            estado="EN_PROGRESO"
        )

        # 3. PostgreSQL Optimización (RST)
        Apunte.objects.create(
            tema=tema_postgres,
            titulo="Optimización de Consultas en PostgreSQL",
            contenido="""
Optimización de Consultas en PostgreSQL
=======================================

PostgreSQL es una de las bases de datos relacionales más potentes y avanzadas. En esta guía veremos cómo optimizar consultas utilizando índices y analizadores.

El Comando EXPLAIN
------------------

Para entender cómo PostgreSQL ejecuta una consulta bajo el capó, usamos la sentencia ``EXPLAIN ANALYZE``. Esto nos indica el plan de ejecución y los tiempos de ejecución reales.

.. code-block:: sql

   EXPLAIN ANALYZE SELECT * FROM gestion_apunte WHERE estado = 'COMPLETADO';

Índices B-Tree
--------------

Los índices por defecto en PostgreSQL son del tipo B-Tree. Deben crearse en columnas que se utilicen con frecuencia en las cláusulas ``WHERE`` y ``JOIN``.

* Ejemplo de creación de un índice:

.. code-block:: sql

   CREATE INDEX idx_apunte_estado ON gestion_apunte (estado);

Índices Parciales
-----------------

Si realizas búsquedas frecuentes de un subconjunto específico de datos, puedes ahorrar espacio y acelerar la indexación usando índices parciales:

.. code-block:: sql

   CREATE INDEX idx_apuntes_completados ON gestion_apunte (fecha_creacion)
   WHERE estado = 'COMPLETADO';
""",
            formato="RST",
            estado="EN_PROGRESO"
        )

        # 4. FastAPI (Markdown)
        Apunte.objects.create(
            tema=tema_fastapi,
            titulo="Primeros pasos con FastAPI y Pydantic v2",
            contenido="""# Primeros pasos con FastAPI

FastAPI es un framework web moderno y rápido para construir APIs con Python basado en tipos estándar de Python.

## Características Clave

* **Rápido:** Rendimiento comparable a NodeJS y Go (gracias a Starlette y Uvicorn).
* **Menos bugs:** Reduce errores humanos en un 40% aproximadamente.
* **Intuitivo:** Gran soporte para autocompletado en IDEs.
* **Fácil:** Diseñado para ser fácil de aprender y usar.

## Hola Mundo en FastAPI

Aquí tienes la implementación básica de una API con FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    nombre: str
    precio: float
    activo: bool = True

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a FastAPI!"}

@app.post("/items/")
def create_item(item: Item):
    return {"status": "item creado", "data": item}
```

Para correr esta aplicación, utiliza:
```bash
uvicorn main:app --reload
```
""",
            formato="MD",
            estado="NO_EMPEZADO"
        )

        # 5. Redis (Markdown)
        Apunte.objects.create(
            tema=tema_redis,
            titulo="Redis como Caché y Almacén en Memoria",
            contenido="""# Redis como Caché y Almacén en Memoria

Redis es un almacenamiento de estructura de datos de clave-valor en memoria de código abierto.

## Casos de Uso Comunes

1. **Caché de consultas:** Almacenar consultas pesadas de bases de datos relacionales para aliviar la carga del servidor de base de datos principal.
2. **Gestión de Sesiones:** Excelente velocidad para validar tokens de sesión en milisegundos.
3. **Colas de Mensajes:** Soporte para estructuras de listas y mecanismos Pub/Sub.

## Ejemplo de uso con Python:

```python
import redis

# Conectar al servidor de Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Setear un valor con tiempo de expiración (TTL) de 60 segundos
r.set('usuario:100:token', 'jwt_token_hash_xyz', ex=60)

# Obtener el valor
token = r.get('usuario:100:token')
print(token) # Output: b'jwt_token_hash_xyz'
```
""",
            formato="MD",
            estado="NO_EMPEZADO"
        )

        self.stdout.write(self.style.SUCCESS("¡Base de datos poblada con éxito!"))
