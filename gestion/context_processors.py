from .models import Categoria

def sidebar_menu(request):
    """
    Context processor para inyectar la jerarquía de categorías y familias 
    en el contexto global de todas las plantillas.
    """
    categorias = Categoria.objects.prefetch_related("familias").all()
    selected_categoria_slug = request.GET.get("categoria", "")
    selected_familia_slug = request.GET.get("familia", "")
    
    return {
        "sidebar_categorias": categorias,
        "selected_categoria_slug": selected_categoria_slug,
        "selected_familia_slug": selected_familia_slug,
    }
