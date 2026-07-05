import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Count, Q, F
from django.http import HttpRequest, HttpResponse
from typing import Any, Dict
from .models import Categoria, Familia, Tema, Apunte, ImagenApunte

logger = logging.getLogger(__name__)

class DashboardView(View):
    """
    Vista para el Dashboard principal.
    Calcula estadísticas de estudio, maneja el buscador global y
    muestra los temas y apuntes pendientes de repaso.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        # Obtener query de búsqueda global
        query = request.GET.get("q", "").strip()
        
        # Filtro de búsqueda global si se especifica
        search_results = None
        if query:
            search_results = Apunte.objects.filter(
                Q(titulo__icontains=query) |
                Q(contenido__icontains=query) |
                Q(tema__nombre__icontains=query) |
                Q(tema__familia__nombre__icontains=query) |
                Q(tema__familia__categoria__nombre__icontains=query)
            ).select_related("tema__familia__categoria").distinct()
            
        # Estadísticas Generales
        total_categorias = Categoria.objects.count()
        total_familias = Familia.objects.count()
        total_temas = Tema.objects.count()
        
        apuntes_qs = Apunte.objects.all()
        total_apuntes = apuntes_qs.count()
        
        no_empezados = apuntes_qs.filter(estado="NO_EMPEZADO").count()
        en_progreso = apuntes_qs.filter(estado="EN_PROGRESO").count()
        completados = apuntes_qs.filter(estado="COMPLETADO").count()
        
        # Calcular porcentaje de progreso general
        progreso_general = 0.0
        if total_apuntes > 0:
            progreso_general = round((completados / total_apuntes) * 100, 1)
            
        # Estadísticas agrupadas por categoría (con optimización de consultas)
        # Obtenemos las categorías anotando el total de apuntes y los completados
        categorias_stats = Categoria.objects.annotate(
            total_apuntes_cat=Count("familias__temas__apuntes"),
            completados_cat=Count(
                "familias__temas__apuntes",
                filter=Q(familias__temas__apuntes__estado="COMPLETADO")
            )
        )
        
        # Calcular porcentaje para cada categoría en memoria
        categorias_data = []
        for cat in categorias_stats:
            porcentaje = 0.0
            if cat.total_apuntes_cat > 0:
                porcentaje = round((cat.completados_cat / cat.total_apuntes_cat) * 100, 1)
            categorias_data.append({
                "categoria": cat,
                "total": cat.total_apuntes_cat,
                "completados": cat.completados_cat,
                "porcentaje": porcentaje
            })
            
        # Módulo de "Temas/Apuntes Pendientes de Repaso"
        # Trae los apuntes en estado 'NO_EMPEZADO' o 'EN_PROGRESO'
        # Usamos select_related para evitar el problema N+1
        apuntes_pendientes = (
            Apunte.objects.filter(estado__in=["NO_EMPEZADO", "EN_PROGRESO"])
            .select_related("tema__familia__categoria")
            .order_by("-fecha_actualizacion")[:10]
        )


        # Temas que tienen apuntes pendientes
        temas_pendientes = (
            Tema.objects.filter(apuntes__estado__in=["NO_EMPEZADO", "EN_PROGRESO"])
            .distinct()
            .select_related("familia__categoria")
            .annotate(
                total_pendientes=Count("apuntes", filter=Q(apuntes__estado__in=["NO_EMPEZADO", "EN_PROGRESO"]))
            )
        )

        context = {
            "query": query,
            "search_results": search_results,
            "total_categorias": total_categorias,
            "total_familias": total_familias,
            "total_temas": total_temas,
            "total_apuntes": total_apuntes,
            "no_empezados": no_empezados,
            "en_progreso": en_progreso,
            "completados": completados,
            "progreso_general": progreso_general,
            "categorias_data": categorias_data,
            "apuntes_pendientes": apuntes_pendientes,
            "temas_pendientes": temas_pendientes,
        }
        
        return render(request, "gestion/dashboard.html", context)


class ApunteDetailView(View):
    """
    Vista de detalle de un Apunte.
    Muestra el contenido compilado y permite actualizar el estado de estudio.
    """
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        # Obtenemos el apunte con select_related y cargando prefetch para sus imágenes
        apunte = get_object_or_404(
            Apunte.objects.select_related("tema__familia__categoria").prefetch_related("imagenes"),
            slug=slug
        )
        
        # Obtener otros apuntes del mismo tema para navegación rápida
        apuntes_relacionados = Apunte.objects.filter(tema=apunte.tema).exclude(id=apunte.id).only("titulo", "slug", "estado")
        
        context = {
            "apunte": apunte,
            "apuntes_relacionados": apuntes_relacionados,
            "estados_choices": Apunte.ESTADOS,
        }
        return render(request, "gestion/apunte_detail.html", context)

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        """
        Permite actualizar el estado de estudio directamente desde el detalle
        mediante un formulario simple.
        """
        apunte = get_object_or_404(Apunte, slug=slug)
        nuevo_estado = request.POST.get("estado")
        
        if nuevo_estado in dict(Apunte.ESTADOS):
            apunte.estado = nuevo_estado
            apunte.save()
            logger.info(f"Estado del apunte '{apunte.titulo}' actualizado a {nuevo_estado}.")
            
        return redirect("gestion:apunte_detail", slug=slug)
