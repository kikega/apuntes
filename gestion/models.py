from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from typing import Any


class Categoria(models.Model):
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


class Tag(models.Model):
    nombre: str = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug: str = models.SlugField(max_length=60, unique=True, blank=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["nombre"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nombre


class Apunte(models.Model):
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
    tags = models.ManyToManyField(Tag, related_name="apuntes", blank=True, verbose_name="Etiquetas")
    relacionado_a = models.ManyToManyField(
        "self", blank=True, symmetrical=False, verbose_name="Apuntes Relacionados"
    )
    favorito: bool = models.BooleanField(default=False, verbose_name="Favorito")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Apunte"
        verbose_name_plural = "Apuntes"
        ordering = ["-fecha_actualizacion"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.titulo)
            count = 1
            while Apunte.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{slugify(self.titulo)}-{count}"
                count += 1
        super().save(*args, **kwargs)

    @property
    def tiempo_lectura(self) -> str:
        palabras = len(self.contenido.split())
        minutos = max(1, round(palabras / 200))
        return f"{minutos} min"

    def __str__(self) -> str:
        return self.titulo


class ImagenApunte(models.Model):
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
