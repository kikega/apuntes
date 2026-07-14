from django.urls import path
from .views import (
    DashboardView,
    ApunteDetailView,
    # AJAX Auxiliar
    FamiliasPorCategoriaView,
    # AJAX Categoría
    CategoriaCreateView,
    CategoriaUpdateView,
    CategoriaDeleteView,
    # AJAX Familia
    FamiliaCreateView,
    FamiliaUpdateView,
    FamiliaDeleteView,
    # AJAX Tema
    TemaCreateView,
    TemaUpdateView,
    TemaDeleteView,
)

app_name = "gestion"

urlpatterns = [
    # Vistas principales
    path("", DashboardView.as_view(), name="dashboard"),
    path("apunte/<slug:slug>/", ApunteDetailView.as_view(), name="apunte_detail"),

    # AJAX Auxiliar
    path("ajax/familias/", FamiliasPorCategoriaView.as_view(), name="ajax_familias_por_categoria"),

    # AJAX CRUD Categoría
    path("ajax/categoria/crear/", CategoriaCreateView.as_view(), name="ajax_categoria_crear"),
    path("ajax/categoria/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="ajax_categoria_editar"),
    path("ajax/categoria/<int:pk>/eliminar/", CategoriaDeleteView.as_view(), name="ajax_categoria_eliminar"),

    # AJAX CRUD Familia
    path("ajax/familia/crear/", FamiliaCreateView.as_view(), name="ajax_familia_crear"),
    path("ajax/familia/<int:pk>/editar/", FamiliaUpdateView.as_view(), name="ajax_familia_editar"),
    path("ajax/familia/<int:pk>/eliminar/", FamiliaDeleteView.as_view(), name="ajax_familia_eliminar"),

    # AJAX CRUD Tema
    path("ajax/tema/crear/", TemaCreateView.as_view(), name="ajax_tema_crear"),
    path("ajax/tema/<int:pk>/editar/", TemaUpdateView.as_view(), name="ajax_tema_editar"),
    path("ajax/tema/<int:pk>/eliminar/", TemaDeleteView.as_view(), name="ajax_tema_eliminar"),
]
