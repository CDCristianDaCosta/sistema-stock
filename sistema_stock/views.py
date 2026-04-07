from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from productos.models import Producto, Negocio
from ventas.models import Venta
from django.db.models import Sum
from datetime import date


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

    ventas_hoy = (
        Venta.objects.filter(negocio=negocio, fecha__date=date.today()).aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    total_productos = Producto.objects.filter(negocio=negocio).count()

    return render(
        request,
        "dashboard.html",
        {"ventas_hoy": ventas_hoy, "total_productos": total_productos},
    )
