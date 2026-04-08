from django.db import models
from django.contrib.auth.models import User


class Negocio(models.Model):
    nombre = models.CharField(max_length=100)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    usuarios = models.ManyToManyField(User, related_name="negocios")


class Producto(models.Model):

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to="productos/", null=True, blank=True)

    def __str__(self):
        return self.nombre
