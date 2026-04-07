from django.urls import path
from .views import nueva_venta, reporte_ventas, ticket, grafico_ventas

urlpatterns = [
    path("", nueva_venta),
    path("reporte/", reporte_ventas),
    path("ticket/<int:venta_id>/", ticket),
    path("grafico/", grafico_ventas),
]
