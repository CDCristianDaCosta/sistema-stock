from django.db import models
from productos.models import Producto, Negocio


class Venta(models.Model):

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Venta {self.id}"


class DetalleVenta(models.Model):

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)

    def subtotal(self):
        return self.cantidad * self.precio
