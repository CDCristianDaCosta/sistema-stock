from django.urls import path
from .views import (
    nueva_venta,
    reporte_ventas,
    ticket,
    grafico_ventas,
    abrir_caja,
    cerrar_caja,
    historial_cajas,
    generar_pdf,
)

urlpatterns = [
    path("", nueva_venta, name="ventas"),
    path("reporte/", reporte_ventas, name="reporte"),
    path("ticket/<int:venta_id>/", ticket, name="ticket"),
    path("grafico/", grafico_ventas, name="grafico"),
    path("caja/abrir/", abrir_caja),
    path("caja/cerrar/", cerrar_caja),
    path("caja/historial/", historial_cajas, name="historial_cajas"),
    path("pdf/<int:venta_id>/", generar_pdf, name="pdf"),
]
