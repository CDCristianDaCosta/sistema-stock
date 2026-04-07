from django.shortcuts import render, redirect

# Create your views here.
from productos.models import Producto, Negocio
from django.contrib.auth.decorators import login_required


def es_admin(user):
    return user.groups.filter(name="Admin").exists()


@login_required
def agregar_producto(request):
    if not es_admin(request.user):
        return redirect("/dashboard/")

    if request.method == "POST":
        nombre = request.POST["nombre"]
        precio = request.POST["precio"]
        stock = request.POST["stock"]

        negocio = Negocio.objects.filter(propietario=request.user).first()

        if not negocio:
            return redirect("/admin/")

        Producto.objects.create(
            nombre=nombre, precio=precio, stock=stock, negocio=negocio
        )

        return redirect("/productos/")

    return render(request, "agregar_producto.html")


def lista_productos(request):

    negocio = Negocio.objects.get(propietario=request.user)

    query = request.GET.get("q")

    productos = Producto.objects.filter(negocio=negocio)

    if query:
        productos = productos.filter(nombre__icontains=query)

    return render(request, "productos.html", {"productos": productos})


def editar_producto(request, id):

    producto = Producto.objects.get(id=id)
    if not es_admin(request.user):
        return redirect("/dashboard/")
    if request.method == "POST":
        producto.nombre = request.POST["nombre"]
        producto.precio = request.POST["precio"]
        producto.stock = request.POST["stock"]
        producto.save()

        return redirect("/productos/")

    return render(request, "editar_producto.html", {"producto": producto})


def eliminar_producto(request, id):
    if not es_admin(request.user):
        return redirect("/dashboard/")
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect("/productos/")
