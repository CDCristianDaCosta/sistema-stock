from django.db import models
from productos.models import Producto, Negocio
from django.contrib.auth.models import User


class Venta(models.Model):
    cliente = models.ForeignKey(
        "productos.Cliente", on_delete=models.SET_NULL, null=True, blank=True
    )
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    caja = models.ForeignKey("Caja", on_delete=models.SET_NULL, null=True, blank=True)
    numero_factura = models.CharField(max_length=50, blank=True)
    timbrado = models.CharField(max_length=50, default="12345678")

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    ganancia = models.IntegerField(default=0)
    TIPO_PAGO = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
    ]

    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO, default="efectivo")
    pago = models.FloatField(default=0)
    vuelto = models.FloatField(default=0)

    def __str__(self):
        return f"Venta {self.id}"


class DetalleVenta(models.Model):

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)

    def subtotal(self):
        return self.cantidad * self.precio


class Caja(models.Model):
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    monto_inicial = models.DecimalField(max_digits=10, decimal_places=0)
    monto_final = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True
    )

    estado = models.CharField(max_length=10, default="abierta")

    def __str__(self):
        return f"Caja {self.id} - {self.estado}"
