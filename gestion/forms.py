from django import forms
from .models import Apunte, Tema, Tag


class ApunteForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors",
        }),
    )
    relacionados = forms.ModelMultipleChoiceField(
        queryset=Apunte.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors",
        }),
    )

    class Meta:
        model = Apunte
        fields = ["tema", "titulo", "formato", "estado", "contenido", "tags", "relacionados"]
        widgets = {
            "tema": forms.Select(attrs={
                "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors"
            }),
            "titulo": forms.TextInput(attrs={
                "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors",
                "placeholder": "Título del apunte..."
            }),
            "formato": forms.Select(attrs={
                "id": "id_formato",
                "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors"
            }),
            "estado": forms.Select(attrs={
                "class": "bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors"
            }),
            "contenido": forms.Textarea(attrs={
                "id": "id_contenido",
                "rows": 15,
                "class": "font-mono bg-white dark:bg-darkCard border border-slate-300 dark:border-darkBorder text-slate-800 dark:text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 focus:outline-none transition-colors resize-y",
                "placeholder": "Escribe tu apunte aquí..."
            }),
        }
