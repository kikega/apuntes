from django.contrib import admin
from .models import Categoria, Familia, Tema, Apunte, ImagenApunte, Tag


class ImagenApunteInline(admin.TabularInline):
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Apunte)
class ApunteAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tema", "estado", "formato", "favorito", "fecha_actualizacion")
    list_filter = ("estado", "formato", "favorito", "tema__familia__categoria", "tema__familia")
    search_fields = ("titulo", "contenido", "tema__nombre")
    prepopulated_fields = {"slug": ("titulo",)}
    filter_horizontal = ("tags", "relacionado_a")
    inlines = [ImagenApunteInline]


@admin.register(ImagenApunte)
class ImagenApunteAdmin(admin.ModelAdmin):
    list_display = ("apunte", "imagen", "descripcion")
    list_filter = ("apunte__tema__familia__categoria", "apunte__tema")
    search_fields = ("descripcion", "apunte__titulo")
