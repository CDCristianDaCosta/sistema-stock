from django.urls import path
from .views import (
    lista_productos,
    agregar_producto,
    editar_producto,
    eliminar_producto,
    lista_clientes,
    agregar_cliente,
    editar_cliente,
    eliminar_cliente,
    lista_proveedores,
    agregar_proveedor,
    eliminar_proveedor,
    lista_compras,
    nueva_compra,
)

urlpatterns = [
    path("", lista_productos),
    path("agregar/", agregar_producto),
    path("editar/<int:id>/", editar_producto),
    path("eliminar/<int:id>/", eliminar_producto),
    path("clientes/", lista_clientes, name="clientes"),
    path("clientes/agregar/", agregar_cliente, name="agregar_cliente"),
    path("clientes/editar/<int:id>/", editar_cliente, name="editar_cliente"),
    path("clientes/eliminar/<int:id>/", eliminar_cliente, name="eliminar_cliente"),
    path("proveedores/", lista_proveedores),
    path("proveedores/agregar/", agregar_proveedor),
    path("proveedores/eliminar/<int:id>/", eliminar_proveedor),
    path("compras/", lista_compras),
    path("compras/nueva/", nueva_compra),
]
