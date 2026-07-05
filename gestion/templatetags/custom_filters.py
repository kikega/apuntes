import logging
from django import template
from django.utils.safestring import mark_safe
from typing import Any

logger = logging.getLogger(__name__)
register = template.Library()

try:
    import markdown
except ImportError:
    markdown = None  # type: ignore

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None  # type: ignore


@register.filter(name="render_content")
def render_content(apunte: Any) -> str:
    """
    Filtro personalizado para renderizar Markdown (.md) o ReStructuredText (.rst)
    de un objeto Apunte y transformarlo en HTML seguro.
    """
    if not apunte:
        return ""

    content: str = apunte.contenido
    formato: str = apunte.formato.upper()

    try:
        if formato == "MD":
            if markdown is None:
                return mark_safe(
                    "<div class='text-amber-500 font-semibold p-2 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900 rounded'>"
                    "Error: El módulo 'markdown' no está instalado. Instalado con pip/uv."
                    "</div>"
                    f"<pre class='mt-2 p-4 bg-slate-100 dark:bg-slate-900 rounded font-mono text-sm overflow-auto'>{content}</pre>"
                )
            
            # Extensiones para mejorar el parseado de Markdown y coloreado de sintaxis
            html = markdown.markdown(
                content,
                extensions=[
                    "extra",          # Soporte para tablas, Markdown inline html, markdown inside html
                    "codehilite",     # Coloreado de sintaxis usando Pygments
                    "fenced_code",    # Soporte para bloques de código cercados ```
                    "toc",            # Tabla de contenidos automática si se incluye [TOC]
                ]
            )
            return mark_safe(html)

        elif formato == "RST":
            if publish_parts is None:
                return mark_safe(
                    "<div class='text-amber-500 font-semibold p-2 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900 rounded'>"
                    "Error: El módulo 'docutils' no está instalado para renderizar RST."
                    "</div>"
                    f"<pre class='mt-2 p-4 bg-slate-100 dark:bg-slate-900 rounded font-mono text-sm overflow-auto'>{content}</pre>"
                )
            
            # Renders ReStructuredText to HTML using docutils
            # writer_name='html4css1' extrae el fragmento de la sección del body
            parts = publish_parts(
                content,
                writer_name="html4css1",
                settings_overrides={"report_level": 5}  # Suprimir advertencias del compilador RST en el HTML
            )
            html = parts.get("html_body", "")
            return mark_safe(html)

        else:
            # Fallback a texto plano seguro
            return mark_safe(
                f"<pre class='p-4 bg-slate-100 dark:bg-slate-900 rounded font-mono text-sm overflow-auto'>{content}</pre>"
            )

    except Exception as e:
        logger.error(f"Error renderizando contenido para el apunte ID {apunte.id}: {e}", exc_info=True)
        return mark_safe(
            f"<div class='text-red-500 font-semibold p-2 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded'>"
            f"Error de renderizado: {e}"
            f"</div>"
            f"<pre class='mt-2 p-4 bg-slate-100 dark:bg-slate-900 rounded font-mono text-sm overflow-auto'>{content}</pre>"
        )
