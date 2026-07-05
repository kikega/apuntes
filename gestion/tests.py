from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from .models import Categoria, Familia, Tema, Apunte
from .templatetags.custom_filters import render_content


class ModelTests(TestCase):
    """
    Pruebas para verificar la correcta inicialización de modelos de datos,
    la jerarquía estricta y la generación automática de slugs.
    """
    def setUp(self) -> None:
        self.cat = Categoria.objects.create(
            nombre="Bases de Datos",
            descripcion="Todo sobre bases de datos SQL y NoSQL"
        )
        self.fam = Familia.objects.create(
            nombre="Relacionales",
            categoria=self.cat,
            descripcion="Motores relacionales como PostgreSQL"
        )
        self.tema = Tema.objects.create(
            nombre="PostgreSQL",
            familia=self.fam,
            descripcion="Uso avanzado de PostgreSQL"
        )

    def test_model_creation(self) -> None:
        """Verifica que los modelos se creen correctamente con sus atributos."""
        self.assertEqual(self.cat.nombre, "Bases de Datos")
        self.assertEqual(self.fam.nombre, "Relacionales")
        self.assertEqual(self.tema.nombre, "PostgreSQL")

    def test_slug_auto_generation(self) -> None:
        """Verifica que el slug se genere automáticamente y sea correcto."""
        self.assertEqual(self.cat.slug, slugify(self.cat.nombre))
        self.assertEqual(self.fam.slug, slugify(self.fam.nombre))
        self.assertEqual(self.tema.slug, slugify(self.tema.nombre))

    def test_slug_uniqueness(self) -> None:
        """Verifica que los slugs duplicados generen un sufijo aleatorio/secuencial."""
        fam2 = Familia.objects.create(
            nombre="Relacionales",
            categoria=self.cat,
            descripcion="Mismo nombre para colisión de slug"
        )
        self.assertNotEqual(self.fam.slug, fam2.slug)
        self.assertTrue(fam2.slug.startswith("relacionales-"))


class FilterTests(TestCase):
    """
    Pruebas para comprobar que el filtro personalizado render_content compile
    de forma segura y correcta Markdown y ReStructuredText a HTML.
    """
    def setUp(self) -> None:
        self.cat = Categoria.objects.create(nombre="Programación")
        self.fam = Familia.objects.create(nombre="Backend", categoria=self.cat)
        self.tema = Tema.objects.create(nombre="Python", familia=self.fam)

    def test_render_markdown(self) -> None:
        """Verifica la compilación de Markdown a HTML."""
        apunte = Apunte.objects.create(
            tema=self.tema,
            titulo="Apuntes de Python",
            contenido="Este es un texto con **negrita** y *cursiva*, y un bloque de código:\n\n```python\nprint('hello')\n```",
            formato="MD"
        )
        rendered = render_content(apunte)
        self.assertIn("<strong>negrita</strong>", rendered)
        self.assertIn("<em>cursiva</em>", rendered)
        self.assertIn("codehilite", rendered)  # Verifica que la extensión de Pygments se aplicó

    def test_render_rst(self) -> None:
        """Verifica la compilación de ReStructuredText a HTML."""
        apunte = Apunte.objects.create(
            tema=self.tema,
            titulo="Documentacion RST",
            contenido="""
Titulo Principal
================

Párrafo introductorio.

* Item de lista 1
* Item de lista 2
""",
            formato="RST"
        )
        rendered = render_content(apunte)
        self.assertIn("<h1 class=\"title\"", rendered)
        self.assertIn("Item de lista 1", rendered)


class ViewTests(TestCase):
    """
    Pruebas de integración para las vistas Dashboard y Detalle de Apunte.
    """
    def setUp(self) -> None:
        self.client = Client()
        self.cat = Categoria.objects.create(nombre="Programación")
        self.fam = Familia.objects.create(nombre="Backend", categoria=self.cat)
        self.tema = Tema.objects.create(nombre="Django", familia=self.fam)
        self.apunte = Apunte.objects.create(
            tema=self.tema,
            titulo="Clases basadas en vistas",
            contenido="La documentación de Django sobre CBV.",
            formato="MD",
            estado="NO_EMPEZADO"
        )

    def test_dashboard_view(self) -> None:
        """Verifica que la página de Dashboard retorne status 200 y contenga estadísticas."""
        url = reverse("gestion:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_categorias"], 1)
        self.assertEqual(response.context["total_apuntes"], 1)
        self.assertEqual(response.context["no_empezados"], 1)

    def test_dashboard_search(self) -> None:
        """Verifica que la barra de búsqueda global filtre los apuntes por contenido."""
        url = reverse("gestion:dashboard")
        # Búsqueda que debe tener éxito
        response = self.client.get(url, {"q": "CBV"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 1)
        
        # Búsqueda que debe fallar
        response_empty = self.client.get(url, {"q": "Inexistente"})
        self.assertEqual(response_empty.status_code, 200)
        self.assertEqual(len(response_empty.context["search_results"]), 0)

    def test_apunte_detail_view(self) -> None:
        """Verifica que el detalle del apunte cargue correctamente."""
        url = reverse("gestion:apunte_detail", kwargs={"slug": self.apunte.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["apunte"], self.apunte)

    def test_apunte_update_status(self) -> None:
        """Verifica que un POST al detalle actualice el estado del apunte."""
        url = reverse("gestion:apunte_detail", kwargs={"slug": self.apunte.slug})
        response = self.client.post(url, {"estado": "COMPLETADO"})
        self.assertEqual(response.status_code, 302)  # Debe redirigir
        
        # Recargar desde la BD y comprobar el estado
        self.apunte.refresh_from_db()
        self.assertEqual(self.apunte.estado, "COMPLETADO")
