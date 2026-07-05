from django.contrib import admin
from .models import Categoria, Familia, Tema, Apunte, ImagenApunte


class ImagenApunteInline(admin.TabularInline):
    """
    Permite subir y gestionar imágenes asociadas al apunte directamente
    desde el formulario de edición del Apunte.
    """
    model = ImagenApunte
    extra = 1
    fields = ("imagen", "descripcion")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "slug")
    list_filter = ("categoria",)
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "familia", "slug")
    list_filter = ("familia__categoria", "familia")
    search_fields = ("nombre", "descripcion", "familia__nombre", "familia__categoria__nombre")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Apunte)
class ApunteAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tema", "estado", "formato", "fecha_actualizacion")
    list_filter = ("estado", "formato", "tema__familia__categoria", "tema__familia")
    search_fields = ("titulo", "contenido", "tema__nombre")
    prepopulated_fields = {"slug": ("titulo",)}
    inlines = [ImagenApunteInline]


@admin.register(ImagenApunte)
class ImagenApunteAdmin(admin.ModelAdmin):
    list_display = ("apunte", "imagen", "descripcion")
    list_filter = ("apunte__tema__familia__categoria", "apunte__tema")
    search_fields = ("descripcion", "apunte__titulo")
