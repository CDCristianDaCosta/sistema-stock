from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from productos.models import Producto, Negocio
from ventas.models import Venta, DetalleVenta
from django.db.models import Sum
from datetime import date
from django.utils.timezone import now


def login_view(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(
                request, "login.html", {"error": "Usuario o contraseña incorrectos"}
            )

    return render(request, "login.html")


@login_required
@login_required
def dashboard(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    if not negocio:
        return redirect("/admin/")

    hoy = now().date()

    mes_actual = hoy.month
    anio_actual = hoy.year

    # ventas hoy
    ventas_hoy = (
        Venta.objects.filter(negocio=negocio, fecha__date=hoy).aggregate(Sum("total"))[
            "total__sum"
        ]
        or 0
    )

    # ventas del mes
    ventas_mes = (
        Venta.objects.filter(
            negocio=negocio, fecha__month=mes_actual, fecha__year=anio_actual
        ).aggregate(Sum("total"))["total__sum"]
        or 0
    )

    # ganancia del mes
    ganancia_mes = (
        Venta.objects.filter(
            negocio=negocio, fecha__month=mes_actual, fecha__year=anio_actual
        ).aggregate(Sum("ganancia"))["ganancia__sum"]
        or 0
    )
    # ventas totales
    ventas_total = (
        Venta.objects.filter(negocio=negocio).aggregate(Sum("total"))["total__sum"] or 0
    )

    # ganancia total
    ganancia = (
        Venta.objects.filter(negocio=negocio).aggregate(Sum("ganancia"))[
            "ganancia__sum"
        ]
        or 0
    )

    # cantidad productos
    cantidad_productos = Producto.objects.filter(negocio=negocio).count()

    # stock bajo
    productos_bajo = Producto.objects.filter(negocio=negocio, stock__lte=5)
    top_productos = (
        DetalleVenta.objects.filter(venta__negocio=negocio)
        .values("producto__nombre")
        .annotate(total=Sum("cantidad"))
        .order_by("-total")[:5]
    )
    return render(
        request,
        "dashboard.html",
        {
            "ventas_hoy": ventas_hoy,
            "ventas_mes": ventas_mes,
            "ganancia_mes": ganancia_mes,
            "cantidad_productos": cantidad_productos,
            "productos_bajo": productos_bajo,
            "top_productos": top_productos,
        },
    )
