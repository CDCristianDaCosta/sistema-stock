from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from productos.models import Producto, Negocio
from ventas.models import Venta
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
def dashboard(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()
    if not negocio:
        return redirect("/admin/")
    ganancia = (
        Venta.objects.filter(negocio=negocio).aggregate(Sum("ganancia"))[
            "ganancia__sum"
        ]
        or 0
    )

    ventas_total = (
        Venta.objects.filter(negocio=negocio).aggregate(Sum("total"))["total__sum"] or 0
    )
    hoy = now().date()
    ventas_hoy = (
        Venta.objects.filter(negocio=negocio, fecha__date=hoy).aggregate(Sum("total"))[
            "total__sum"
        ]
        or 0
    )

    # 📦 productos bajo stock
    productos_bajo = Producto.objects.filter(negocio=negocio, stock__lte=5)

    return render(
        request,
        "dashboard.html",
        {
            "ventas_total": ventas_total,
            "ganancia": ganancia,
            "ventas_hoy": ventas_hoy,
            "productos_bajo": productos_bajo,
        },
    )
