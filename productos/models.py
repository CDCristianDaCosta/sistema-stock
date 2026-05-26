from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Negocio(models.Model):
    nombre = models.CharField(max_length=100)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    usuarios = models.ManyToManyField(User, related_name="negocios")

    def __str__(self):
        return self.nombre


class Producto(models.Model):

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to="productos/", null=True, blank=True)
    imagen = CloudinaryField("imagen", blank=True, null=True)
    costo = models.IntegerField(default=0)

    @property
    def margen(self):
        if self.costo > 0:
            return round(((self.precio - self.costo) / self.costo) * 100, 1)
        return 0


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, blank=True, null=True)  # CI o RUC
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    proveedor = models.ForeignKey("Proveedor", on_delete=models.CASCADE)
    negocio = models.ForeignKey("Negocio", on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)

    def __str__(self):
        return f"Compra {self.id}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey("Producto", on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.IntegerField()
