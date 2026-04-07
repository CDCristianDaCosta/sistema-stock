from django.shortcuts import render, redirect
from productos.models import Producto
from .models import Venta, DetalleVenta
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from productos.models import Negocio
from django.contrib.auth.decorators import login_required


@login_required
def nueva_venta(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()
    if not negocio:
        return redirect("/admin/")

    query = request.GET.get("q")

    productos = Producto.objects.filter(negocio=negocio)

    if query:
        productos = productos.filter(nombre__icontains=query)

    if request.method == "POST":

        total = 0

        venta = Venta.objects.create(negocio=negocio, total=0)

        for key in request.POST:

            if key.startswith("cantidad_"):

                id_producto = key.split("_")[1]
                cantidad = int(request.POST[key])

                if cantidad > 0:

                    producto = Producto.objects.get(id=id_producto)

                    subtotal = producto.precio * cantidad
                    total += subtotal

                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio=producto.precio,
                    )

                    producto.stock -= cantidad
                    producto.save()

        venta.total = total
        venta.save()

        return redirect(f"/ventas/ticket/{venta.id}")

    return render(request, "ventas.html", {"productos": productos})


def reporte_ventas(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    ventas = Venta.objects.filter(negocio=negocio)

    return render(request, "reporte.html", {"ventas": ventas})


def ticket(request, venta_id):

    venta = Venta.objects.get(id=venta_id)

    detalles = DetalleVenta.objects.filter(venta=venta)

    return render(request, "ticket.html", {"venta": venta, "detalles": detalles})


def grafico_ventas(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()
    ventas = (
        Venta.objects.filter(negocio=negocio)
        .annotate(dia=TruncDate("fecha"))
        .values("dia")
        .annotate(total=Sum("total"))
        .order_by("dia")
    )

    labels = []
    data = []

    for v in ventas:
        labels.append(v["dia"].strftime("%d-%m"))
        data.append(float(v["total"]))

    return render(request, "grafico.html", {"labels": labels, "data": data})
