import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.text import slugify
from typing import Any, Dict
from .models import Categoria, Familia, Tema, Apunte, ImagenApunte
from .forms import ApunteForm
from .templatetags.custom_filters import render_content

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dashboard Principal
# ---------------------------------------------------------------------------

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

        # Filtrado de Temas para el Explorador
        selected_categoria_slug = request.GET.get("categoria", "")
        selected_familia_slug = request.GET.get("familia", "")
        
        selected_categoria = None
        selected_familia = None
        
        temas_qs = Tema.objects.select_related("familia__categoria").prefetch_related("apuntes").all()
        
        if selected_categoria_slug:
            selected_categoria = get_object_or_404(Categoria, slug=selected_categoria_slug)
            temas_qs = temas_qs.filter(familia__categoria=selected_categoria)
        elif selected_familia_slug:
            selected_familia = get_object_or_404(Familia, slug=selected_familia_slug)
            temas_qs = temas_qs.filter(familia=selected_familia)

        # Datos para el panel de gestión (todos los registros ordenados)
        categorias_list = Categoria.objects.order_by("nombre")
        familias_list = Familia.objects.select_related("categoria").order_by("categoria__nombre", "nombre")
        temas_list = Tema.objects.select_related("familia__categoria").order_by(
            "familia__categoria__nombre", "familia__nombre", "nombre"
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
            "temas_explorador": temas_qs,
            "selected_categoria": selected_categoria,
            "selected_familia": selected_familia,
            # Datos para el panel de gestión de taxonomía
            "categorias_list": categorias_list,
            "familias_list": familias_list,
            "temas_list": temas_list,
        }
        
        return render(request, "gestion/dashboard.html", context)


# ---------------------------------------------------------------------------
# Apunte Detail
# ---------------------------------------------------------------------------

class ApunteDetailView(View):
    """
    Vista de detalle de un Apunte.
    Muestra el contenido compilado y permite actualizar el estado de estudio.
    """
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        apunte = get_object_or_404(
            Apunte.objects.select_related("tema__familia__categoria").prefetch_related("imagenes"),
            slug=slug
        )
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


# ---------------------------------------------------------------------------
# Helpers AJAX
# ---------------------------------------------------------------------------

def _get_post_data(request: HttpRequest) -> Dict[str, Any]:
    """Parsea el body JSON de una petición AJAX."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


def _slug_unico(model_class, base_slug: str, exclude_id: int | None = None) -> str:
    """Genera un slug único para el modelo dado, añadiendo sufijo numérico si es necesario."""
    slug = base_slug
    count = 1
    qs = model_class.objects.filter(slug=slug)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    while qs.exists():
        slug = f"{base_slug}-{count}"
        count += 1
        qs = model_class.objects.filter(slug=slug)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
    return slug


# ---------------------------------------------------------------------------
# AJAX: Auxiliar — Familias por Categoría (para carga dinámica en modales)
# ---------------------------------------------------------------------------

class FamiliasPorCategoriaView(View):
    """
    GET /ajax/familias/?categoria_id=<id>
    Retorna la lista de Familias de una Categoría para carga dinámica en selects.
    """
    def get(self, request: HttpRequest) -> JsonResponse:
        categoria_id = request.GET.get("categoria_id")
        if not categoria_id:
            return JsonResponse({"familias": []})
        familias = (
            Familia.objects.filter(categoria_id=categoria_id)
            .order_by("nombre")
            .values("id", "nombre")
        )
        return JsonResponse({"familias": list(familias)})


# ---------------------------------------------------------------------------
# AJAX: CRUD Categoría
# ---------------------------------------------------------------------------

class CategoriaCreateView(View):
    """POST /ajax/categoria/crear/ — Crea una nueva Categoría."""
    def post(self, request: HttpRequest) -> JsonResponse:
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        slug_custom = data.get("slug", "").strip()

        if not nombre:
            return JsonResponse({"success": False, "errors": {"nombre": "El nombre es obligatorio."}}, status=400)

        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({"success": False, "errors": {"nombre": f"Ya existe una categoría con el nombre '{nombre}'."}}, status=400)

        base_slug = slugify(slug_custom) if slug_custom else slugify(nombre)
        slug_final = _slug_unico(Categoria, base_slug)

        try:
            cat = Categoria.objects.create(nombre=nombre, slug=slug_final, descripcion=descripcion)
            logger.info(f"Categoría creada: '{cat.nombre}' (id={cat.id})")
            return JsonResponse({
                "success": True,
                "message": f"Categoría '{cat.nombre}' creada correctamente.",
                "item": {"id": cat.id, "nombre": cat.nombre, "slug": cat.slug, "descripcion": cat.descripcion}
            }, status=201)
        except Exception as e:
            logger.error(f"Error al crear categoría: {e}")
            return JsonResponse({"success": False, "errors": {"__all__": "Error interno al guardar. Inténtalo de nuevo."}}, status=500)


class CategoriaUpdateView(View):
    """POST /ajax/categoria/<id>/editar/ — Edita una Categoría existente."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        cat = get_object_or_404(Categoria, pk=pk)
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        slug_custom = data.get("slug", "").strip()

        if not nombre:
            return JsonResponse({"success": False, "errors": {"nombre": "El nombre es obligatorio."}}, status=400)

        if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
            return JsonResponse({"success": False, "errors": {"nombre": f"Ya existe otra categoría con el nombre '{nombre}'."}}, status=400)

        cat.nombre = nombre
        cat.descripcion = descripcion
        if slug_custom:
            cat.slug = _slug_unico(Categoria, slugify(slug_custom), exclude_id=pk)
        cat.save()

        logger.info(f"Categoría actualizada: '{cat.nombre}' (id={cat.id})")
        return JsonResponse({
            "success": True,
            "message": f"Categoría '{cat.nombre}' actualizada correctamente.",
            "item": {"id": cat.id, "nombre": cat.nombre, "slug": cat.slug, "descripcion": cat.descripcion}
        })


class CategoriaDeleteView(View):
    """POST /ajax/categoria/<id>/eliminar/ — Elimina una Categoría y sus dependencias en cascada."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        cat = get_object_or_404(Categoria, pk=pk)
        nombre = cat.nombre

        # Contar el impacto en cascada antes de eliminar
        total_familias = cat.familias.count()
        total_temas = Tema.objects.filter(familia__categoria=cat).count()
        total_apuntes = Apunte.objects.filter(tema__familia__categoria=cat).count()

        cat.delete()
        logger.warning(f"Categoría eliminada: '{nombre}' (familias={total_familias}, temas={total_temas}, apuntes={total_apuntes})")
        return JsonResponse({
            "success": True,
            "message": f"Categoría '{nombre}' eliminada. Se eliminaron también {total_familias} familia(s), {total_temas} tema(s) y {total_apuntes} apunte(s).",
            "deleted_id": pk
        })


# ---------------------------------------------------------------------------
# AJAX: CRUD Familia
# ---------------------------------------------------------------------------

class FamiliaCreateView(View):
    """POST /ajax/familia/crear/ — Crea una nueva Familia."""
    def post(self, request: HttpRequest) -> JsonResponse:
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        categoria_id = data.get("categoria_id")
        slug_custom = data.get("slug", "").strip()

        errors: Dict[str, str] = {}
        if not nombre:
            errors["nombre"] = "El nombre es obligatorio."
        if not categoria_id:
            errors["categoria_id"] = "Debes seleccionar una categoría."

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        categoria = get_object_or_404(Categoria, pk=categoria_id)
        base_slug = slugify(slug_custom) if slug_custom else slugify(nombre)
        slug_final = _slug_unico(Familia, base_slug)

        try:
            familia = Familia.objects.create(
                nombre=nombre, slug=slug_final, categoria=categoria, descripcion=descripcion
            )
            logger.info(f"Familia creada: '{familia.nombre}' en '{categoria.nombre}' (id={familia.id})")
            return JsonResponse({
                "success": True,
                "message": f"Familia '{familia.nombre}' creada en '{categoria.nombre}'.",
                "item": {
                    "id": familia.id, "nombre": familia.nombre, "slug": familia.slug,
                    "descripcion": familia.descripcion,
                    "categoria_id": categoria.id, "categoria_nombre": categoria.nombre
                }
            }, status=201)
        except Exception as e:
            logger.error(f"Error al crear familia: {e}")
            return JsonResponse({"success": False, "errors": {"__all__": "Error interno al guardar."}}, status=500)


class FamiliaUpdateView(View):
    """POST /ajax/familia/<id>/editar/ — Edita una Familia existente."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        familia = get_object_or_404(Familia, pk=pk)
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        categoria_id = data.get("categoria_id")
        slug_custom = data.get("slug", "").strip()

        errors: Dict[str, str] = {}
        if not nombre:
            errors["nombre"] = "El nombre es obligatorio."
        if not categoria_id:
            errors["categoria_id"] = "Debes seleccionar una categoría."

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        categoria = get_object_or_404(Categoria, pk=categoria_id)
        familia.nombre = nombre
        familia.descripcion = descripcion
        familia.categoria = categoria
        if slug_custom:
            familia.slug = _slug_unico(Familia, slugify(slug_custom), exclude_id=pk)
        familia.save()

        logger.info(f"Familia actualizada: '{familia.nombre}' (id={familia.id})")
        return JsonResponse({
            "success": True,
            "message": f"Familia '{familia.nombre}' actualizada correctamente.",
            "item": {
                "id": familia.id, "nombre": familia.nombre, "slug": familia.slug,
                "descripcion": familia.descripcion,
                "categoria_id": categoria.id, "categoria_nombre": categoria.nombre
            }
        })


class FamiliaDeleteView(View):
    """POST /ajax/familia/<id>/eliminar/ — Elimina una Familia y sus dependencias."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        familia = get_object_or_404(Familia, pk=pk)
        nombre = familia.nombre
        categoria_nombre = familia.categoria.nombre

        total_temas = familia.temas.count()
        total_apuntes = Apunte.objects.filter(tema__familia=familia).count()

        familia.delete()
        logger.warning(f"Familia eliminada: '{nombre}' de '{categoria_nombre}' (temas={total_temas}, apuntes={total_apuntes})")
        return JsonResponse({
            "success": True,
            "message": f"Familia '{nombre}' eliminada. Se eliminaron también {total_temas} tema(s) y {total_apuntes} apunte(s).",
            "deleted_id": pk
        })


# ---------------------------------------------------------------------------
# AJAX: CRUD Tema
# ---------------------------------------------------------------------------

class TemaCreateView(View):
    """POST /ajax/tema/crear/ — Crea un nuevo Tema."""
    def post(self, request: HttpRequest) -> JsonResponse:
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        familia_id = data.get("familia_id")
        slug_custom = data.get("slug", "").strip()

        errors: Dict[str, str] = {}
        if not nombre:
            errors["nombre"] = "El nombre es obligatorio."
        if not familia_id:
            errors["familia_id"] = "Debes seleccionar una familia."

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        familia = get_object_or_404(Familia, pk=familia_id)
        base_slug = slugify(slug_custom) if slug_custom else slugify(nombre)
        slug_final = _slug_unico(Tema, base_slug)

        try:
            tema = Tema.objects.create(
                nombre=nombre, slug=slug_final, familia=familia, descripcion=descripcion
            )
            logger.info(f"Tema creado: '{tema.nombre}' en '{familia.nombre}' (id={tema.id})")
            return JsonResponse({
                "success": True,
                "message": f"Tema '{tema.nombre}' creado en '{familia.nombre}'.",
                "item": {
                    "id": tema.id, "nombre": tema.nombre, "slug": tema.slug,
                    "descripcion": tema.descripcion,
                    "familia_id": familia.id, "familia_nombre": familia.nombre,
                    "categoria_nombre": familia.categoria.nombre
                }
            }, status=201)
        except Exception as e:
            logger.error(f"Error al crear tema: {e}")
            return JsonResponse({"success": False, "errors": {"__all__": "Error interno al guardar."}}, status=500)


class TemaUpdateView(View):
    """POST /ajax/tema/<id>/editar/ — Edita un Tema existente."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        tema = get_object_or_404(Tema, pk=pk)
        data = _get_post_data(request)
        nombre = data.get("nombre", "").strip()
        descripcion = data.get("descripcion", "").strip()
        familia_id = data.get("familia_id")
        slug_custom = data.get("slug", "").strip()

        errors: Dict[str, str] = {}
        if not nombre:
            errors["nombre"] = "El nombre es obligatorio."
        if not familia_id:
            errors["familia_id"] = "Debes seleccionar una familia."

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        familia = get_object_or_404(Familia, pk=familia_id)
        tema.nombre = nombre
        tema.descripcion = descripcion
        tema.familia = familia
        if slug_custom:
            tema.slug = _slug_unico(Tema, slugify(slug_custom), exclude_id=pk)
        tema.save()

        logger.info(f"Tema actualizado: '{tema.nombre}' (id={tema.id})")
        return JsonResponse({
            "success": True,
            "message": f"Tema '{tema.nombre}' actualizado correctamente.",
            "item": {
                "id": tema.id, "nombre": tema.nombre, "slug": tema.slug,
                "descripcion": tema.descripcion,
                "familia_id": familia.id, "familia_nombre": familia.nombre,
                "categoria_nombre": familia.categoria.nombre
            }
        })


class TemaDeleteView(View):
    """POST /ajax/tema/<id>/eliminar/ — Elimina un Tema y sus apuntes."""
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        tema = get_object_or_404(Tema, pk=pk)
        nombre = tema.nombre
        familia_nombre = tema.familia.nombre

        total_apuntes = tema.apuntes.count()

        tema.delete()
        logger.warning(f"Tema eliminado: '{nombre}' de '{familia_nombre}' (apuntes={total_apuntes})")
        return JsonResponse({
            "success": True,
            "message": f"Tema '{nombre}' eliminado. Se eliminaron también {total_apuntes} apunte(s).",
            "deleted_id": pk
        })


# ---------------------------------------------------------------------------
# CRUD de Apuntes (Crear, Editar, Vista Previa)
# ---------------------------------------------------------------------------

class ApunteCreateView(View):
    """
    Vista para crear un nuevo Apunte.
    Permite pre-seleccionar el tema pasando `tema` como parámetro GET.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        tema_id = request.GET.get("tema")
        initial_data = {}
        if tema_id:
            try:
                tema = Tema.objects.get(pk=tema_id)
                initial_data["tema"] = tema
            except Tema.DoesNotExist:
                pass

        form = ApunteForm(initial=initial_data)
        context = {
            "form": form,
            "action": "Crear",
            "is_create": True,
        }
        return render(request, "gestion/apunte_form.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ApunteForm(request.POST)
        if form.is_valid():
            apunte = form.save()
            logger.info(f"Apunte creado: '{apunte.titulo}' (id={apunte.id})")
            return redirect("gestion:apunte_detail", slug=apunte.slug)

        context = {
            "form": form,
            "action": "Crear",
            "is_create": True,
        }
        return render(request, "gestion/apunte_form.html", context)


class ApunteUpdateView(View):
    """
    Vista para editar un Apunte existente.
    Carga el apunte por su slug y actualiza sus campos.
    """
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        apunte = get_object_or_404(Apunte, slug=slug)
        form = ApunteForm(instance=apunte)
        context = {
            "form": form,
            "action": "Editar",
            "is_create": False,
            "apunte": apunte,
        }
        return render(request, "gestion/apunte_form.html", context)

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        apunte = get_object_or_404(Apunte, slug=slug)
        form = ApunteForm(request.POST, instance=apunte)
        if form.is_valid():
            apunte = form.save()
            logger.info(f"Apunte actualizado: '{apunte.titulo}' (id={apunte.id})")
            return redirect("gestion:apunte_detail", slug=apunte.slug)

        context = {
            "form": form,
            "action": "Editar",
            "is_create": False,
            "apunte": apunte,
        }
        return render(request, "gestion/apunte_form.html", context)


class ApuntePreviewView(View):
    """
    Vista AJAX para compilar contenido Markdown o RST en tiempo real.
    No persiste cambios en base de datos.
    """
    def post(self, request: HttpRequest) -> HttpResponse:
        contenido = request.POST.get("contenido", "")
        formato = request.POST.get("formato", "MD")
        apunte_id = request.POST.get("apunte_id")

        if apunte_id:
            try:
                apunte = Apunte.objects.get(pk=apunte_id)
                apunte.contenido = contenido
                apunte.formato = formato
            except Apunte.DoesNotExist:
                apunte = Apunte(contenido=contenido, formato=formato)
        else:
            apunte = Apunte(contenido=contenido, formato=formato)

        html = render_content(apunte)
        return HttpResponse(html)
