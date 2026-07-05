from django.urls import path
from .views import DashboardView, ApunteDetailView

app_name = "gestion"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("apunte/<slug:slug>/", ApunteDetailView.as_view(), name="apunte_detail"),
]
