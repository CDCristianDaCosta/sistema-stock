from django.urls import path
from .views import lista_productos, agregar_producto, editar_producto, eliminar_producto

urlpatterns = [
    path("", lista_productos),
    path("agregar/", agregar_producto),
    path("editar/<int:id>/", editar_producto),
    path("eliminar/<int:id>/", eliminar_producto),
]
