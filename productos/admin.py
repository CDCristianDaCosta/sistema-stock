from django.contrib import admin
from .models import Producto, Negocio, Cliente


admin.site.register(Producto)
admin.site.register(Negocio)
admin.site.register(Cliente)
