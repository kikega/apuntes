from django.db import models
from django.utils.text import slugify
from typing import Any

class Categoria(models.Model):
    """
    Representa una categoría principal para organizar los apuntes (ej. Programación, Bases de Datos).
    """
    nombre: str = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug: str = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    descripcion: str = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nombre


class Familia(models.Model):
    """
    Representa una familia o subcategoría dentro de una categoría principal (ej. Backend, Frontend).
    """
    nombre: str = models.CharField(max_length=100, verbose_name="Nombre")
    slug: str = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    categoria: Categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="familias", verbose_name="Categoría"
    )
    descripcion: str = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Familia / Subcategoría"
        verbose_name_plural = "Familias / Subcategorías"
        ordering = ["categoria", "nombre"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            base_slug = slugify(self.nombre)
            self.slug = base_slug
            count = 1
            while Familia.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.categoria.nombre} ➔ {self.nombre}"


class Tema(models.Model):
    """
    Representa un tema específico dentro de una familia (ej. Django, FastAPI).
    """
    nombre: str = models.CharField(max_length=100, verbose_name="Nombre")
    slug: str = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    familia: Familia = models.ForeignKey(
        Familia, on_delete=models.CASCADE, related_name="temas", verbose_name="Familia"
    )
    descripcion: str = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ["familia", "nombre"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            base_slug = slugify(self.nombre)
            self.slug = base_slug
            count = 1
            while Tema.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.familia.nombre} ➔ {self.nombre}"


class Apunte(models.Model):
    """
    Representa el fichero o apunte técnico en sí, conteniendo el contenido en Markdown/RST.
    """
    ESTADOS = [
        ("NO_EMPEZADO", "No empezado"),
        ("EN_PROGRESO", "En progreso"),
        ("COMPLETADO", "Completado"),
    ]
    FORMATOS = [
        ("MD", "Markdown"),
        ("RST", "ReStructuredText"),
    ]

    tema: Tema = models.ForeignKey(
        Tema, on_delete=models.CASCADE, related_name="apuntes", verbose_name="Tema"
    )
    titulo: str = models.CharField(max_length=200, verbose_name="Título")
    slug: str = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    contenido: str = models.TextField(verbose_name="Contenido")
    formato: str = models.CharField(
        max_length=5, choices=FORMATOS, default="MD", verbose_name="Formato de Texto"
    )
    estado: str = models.CharField(
        max_length=15, choices=ESTADOS, default="NO_EMPEZADO", verbose_name="Estado de Estudio"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Apunte"
        verbose_name_plural = "Apuntes"
        ordering = ["-fecha_actualizacion"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            base_slug = slugify(self.titulo)
            self.slug = base_slug
            count = 1
            while Apunte.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.titulo


class ImagenApunte(models.Model):
    """
    Almacena las imágenes locales asociadas a un apunte para poder renderizarlas.
    """
    apunte: Apunte = models.ForeignKey(
        Apunte, on_delete=models.CASCADE, related_name="imagenes", verbose_name="Apunte"
    )
    imagen = models.ImageField(upload_to="apuntes_imagenes/", verbose_name="Imagen")
    descripcion: str = models.CharField(
        max_length=255, blank=True, verbose_name="Descripción / Alt Text"
    )

    class Meta:
        verbose_name = "Imagen de Apunte"
        verbose_name_plural = "Imágenes de Apunte"

    def __str__(self) -> str:
        return f"Imagen para {self.apunte.titulo} ({self.imagen.name})"
