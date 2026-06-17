from django.shortcuts import render, redirect

# Create your views here.
from productos.models import Producto, Negocio, Cliente, Proveedor
from .models import Compra, DetalleCompra
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
import openpyxl


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
        imagen = request.FILES.get("imagen")
        codigo = request.POST["codigo"]
        costo = request.POST["costo"]

        negocio = Negocio.objects.filter(propietario=request.user).first()

        if not negocio:
            return redirect("/admin/")

        Producto.objects.create(
            nombre=nombre,
            precio=precio,
            stock=stock,
            imagen=imagen,
            negocio=negocio,
            codigo=codigo,
            costo=costo,
        )

        return redirect("/productos/")

    return render(request, "agregar_producto.html")


def lista_productos(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    query = request.GET.get("q")

    productos = Producto.objects.filter(negocio=negocio)

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )

    return render(request, "productos.html", {"productos": productos, "query": query})


def editar_producto(request, id):

    producto = Producto.objects.get(id=id)
    if not es_admin(request.user):
        return redirect("/dashboard/")
    if request.method == "POST":
        producto.nombre = request.POST.get("nombre", "")
        producto.precio = request.POST.get("precio") or 0
        producto.stock = request.POST.get("stock") or 0
        producto.costo = request.POST.get("costo") or 0
        imagen = request.FILES.get("imagen")

        imagen = request.FILES.get("imagen")
        if imagen:
            producto.imagen = imagen

        producto.save()

        return redirect("/productos/")

    return render(request, "editar_producto.html", {"producto": producto})


def eliminar_producto(request, id):
    if not es_admin(request.user):
        return redirect("/dashboard/")
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect("/productos/")


@login_required
def lista_clientes(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    query = request.GET.get("q")

    clientes = Cliente.objects.filter(negocio=negocio)

    if query:
        clientes = clientes.filter(nombre__icontains=query)

    return render(request, "clientes.html", {"clientes": clientes})


@login_required
def agregar_cliente(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    if request.method == "POST":
        nombre = request.POST["nombre"]
        documento = request.POST["documento"]

        Cliente.objects.create(nombre=nombre, documento=documento, negocio=negocio)

        return redirect("/productos/clientes/")

    return render(request, "agregar_cliente.html")


@login_required
def editar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)

    if request.method == "POST":
        cliente.nombre = request.POST["nombre"]
        cliente.documento = request.POST["documento"]
        cliente.save()

        return redirect("/productos/clientes/")

    return render(request, "editar_cliente.html", {"cliente": cliente})


@login_required
def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    cliente.delete()
    return redirect("/productos/clientes/")


@login_required
def lista_proveedores(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()
    proveedores = Proveedor.objects.filter(negocio=negocio)
    return render(request, "proveedores.html", {"proveedores": proveedores})


@login_required
def agregar_proveedor(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    if request.method == "POST":
        Proveedor.objects.create(
            nombre=request.POST["nombre"],
            telefono=request.POST["telefono"],
            direccion=request.POST["direccion"],
            negocio=negocio,
        )
        return redirect("/productos/proveedores/")

    return render(request, "agregar_proveedor.html")


@login_required
def editar_proveedor(request, id):

    proveedor = Proveedor.objects.get(id=id)

    if request.method == "POST":

        proveedor.nombre = request.POST["nombre"]
        proveedor.telefono = request.POST["telefono"]
        proveedor.direccion = request.POST["direccion"]

        proveedor.save()

        return redirect("/productos/proveedores/")

    return render(
        request,
        "editar_proveedor.html",
        {"proveedor": proveedor},
    )


@login_required
def eliminar_proveedor(request, id):
    proveedor = Proveedor.objects.get(id=id)
    proveedor.delete()
    return redirect("/productos/proveedores/")


@login_required
def lista_compras(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()
    compras = Compra.objects.filter(negocio=negocio)
    return render(request, "compras.html", {"compras": compras})


@login_required
def nueva_compra(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    productos = Producto.objects.filter(negocio=negocio)
    proveedores = Proveedor.objects.filter(negocio=negocio)

    if request.method == "POST":

        # ✅ TODO VA DENTRO DEL POST
        producto_id = request.POST.get("producto")
        proveedor_id = request.POST.get("proveedor")
        cantidad = int(request.POST.get("cantidad", 0))
        precio = float(request.POST.get("precio", 0))

        producto = Producto.objects.filter(id=producto_id).first()
        proveedor = Proveedor.objects.filter(id=proveedor_id).first()

        if not producto or not proveedor:
            return redirect("/productos/compras/nueva/")

        total = cantidad * precio

        # 🧾 CABECERA
        compra = Compra.objects.create(
            proveedor=proveedor, negocio=negocio, total=total
        )

        # 📦 DETALLE
        DetalleCompra.objects.create(
            compra=compra, producto=producto, cantidad=cantidad, precio=precio
        )

        # 📈 STOCK
        producto.stock += cantidad
        producto.save()

        return redirect("/productos/compras/")

    # 👉 GET (abrir página)
    return render(
        request,
        "nueva_compra.html",
        {"productos": productos, "proveedores": proveedores},
    )


@login_required
def exportar_excel(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    productos = Producto.objects.filter(negocio=negocio)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Productos"

    headers = ["Nombre", "Código", "Precio", "Costo", "Stock"]

    sheet.append(headers)

    for p in productos:
        sheet.append([p.nombre, p.codigo, p.precio, p.costo, p.stock])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="productos.xlsx"'

    workbook.save(response)

    return response
