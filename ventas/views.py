from django.shortcuts import render, redirect
from productos.models import Producto, Cliente, Negocio
from .models import Venta, DetalleVenta
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils.timezone import now
from .models import Caja
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def generar_pdf(request, venta_id):

    venta = Venta.objects.get(id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    negocio = venta.negocio

    template = get_template("ticket.html")
    html = template.render({
    "venta": venta,
    "detalles": detalles,
    "negocio": negocio,
})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=venta_{venta.id}.pdf"

    pisa.CreatePDF(html, dest=response)

    return response


@login_required
def nueva_venta(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    if not negocio:
        return redirect("/admin/")

    clientes = Cliente.objects.filter(negocio=negocio)
    productos = Producto.objects.filter(negocio=negocio)

    # 🔐 Validar caja abierta
    caja_abierta = Caja.objects.filter(negocio=negocio, estado="abierta").first()

    if not caja_abierta:
        return redirect("/ventas/caja/abrir/")

    # 🔥 SOLO SI ES POST
    if request.method == "POST":

        cliente_id = request.POST.get("cliente")
        cliente = Cliente.objects.filter(id=cliente_id).first() if cliente_id else None

        total = 0
        ganancia_total = 0

        venta = Venta.objects.create(
            negocio=negocio,
            total=0,
            ganancia=0,
            cliente=cliente,
            caja=caja_abierta,
        )

        for key, value in request.POST.items():

            if key.startswith("cantidad_"):

                id_producto = key.split("_")[1]
                cantidad = int(value)

                if cantidad > 0:

                    producto = Producto.objects.filter(id=id_producto).first()

                    if not producto:
                        continue

                    if producto.stock < cantidad:
                        continue

                    subtotal = producto.precio * cantidad
                    total += subtotal

                    ganancia_producto = (
    (float(producto.precio) - float(producto.costo))
    * cantidad
)

                    ganancia_total += ganancia_producto

                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio=producto.precio,
                    )

                    producto.stock -= cantidad
                    producto.save()

        # 🚫 evitar venta vacía
        if total == 0:
            venta.delete()
            return redirect("/ventas/")

        # 💰 validar pago
        pago = Decimal(request.POST.get("pago", 0))
        tipo_pago = request.POST.get("tipo_pago")

        descuento = request.POST.get("descuento", "0")
        descuento = Decimal(str(descuento).replace(".", ""))

        # total final con descuento
        total_final = total - descuento

        # descuento afecta ganancia UNA sola vez
        ganancia_total -= float(descuento)

        if total_final < 0:
            total_final = 0
        if pago < total_final:
            venta.delete()
            return redirect("/ventas/")

        # 🧾 NUMERO FACTURA (DENTRO DEL POST)
        ultima = Venta.objects.order_by("-id").first()

        if ultima and ultima.numero_factura:
            numero = int(ultima.numero_factura.split("-")[-1]) + 1
        else:
            numero = 1

        numero_factura = (
    f"{negocio.establecimiento}-"
    f"{negocio.punto_expedicion}-"
    f"{str(numero).zfill(7)}"
)

        # 💾 guardar datos finales
        venta.total = total_final
        venta.ganancia = max(0, int(ganancia_total))    
        venta.numero_factura = numero_factura
        venta.timbrado = "12345678"
        venta.pago = pago
        venta.tipo_pago = tipo_pago
        venta.vuelto = pago - total_final
        venta.descuento = descuento
        venta.save()

        return redirect("ticket", venta_id=venta.id)

    # 🔵 GET (cuando abre la pantalla)
    return render(
        request,
        "ventas.html",
        {
            "productos": productos,
            "clientes": clientes,
        },
    )


@login_required
@login_required
def reporte_ventas(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    ventas = Venta.objects.filter(negocio=negocio).order_by("-fecha")

    total_vendido = ventas.aggregate(Sum("total"))["total__sum"] or 0

    total_ganancia = ventas.aggregate(Sum("ganancia"))["ganancia__sum"] or 0

    return render(
        request,
        "reporte.html",
        {
            "ventas": ventas,
            "total_vendido": total_vendido,
            "total_ganancia": total_ganancia,
        },
    )


@login_required
def ticket(request, venta_id):

    venta = Venta.objects.get(id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    negocio = venta.negocio

    return render(
        request,
        "ticket.html",
        {
            "venta": venta,
            "detalles": detalles,
            "negocio": negocio,
        },
    )

@login_required
def grafico_ventas(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    ventas = (
        Venta.objects.filter(negocio=negocio)
        .annotate(dia=TruncDate("fecha"))
        .values("dia")
        .annotate(total=Sum("total"))
        .order_by("dia")
    )
    top_productos = (
        DetalleVenta.objects.values("producto__nombre")
        .annotate(total=Sum("cantidad"))
        .order_by("-total")[:5]
    )
    labels = []
    data = []

    for v in ventas:
        labels.append(v["dia"].strftime("%d-%m"))
        data.append(float(v["total"]))

    return render(request, "grafico.html", {"labels": labels, "data": data})


@login_required
def abrir_caja(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    caja_abierta = Caja.objects.filter(negocio=negocio, estado="abierta").first()

    if caja_abierta:
        return redirect("/ventas/")

    if request.method == "POST":

        monto_inicial = float(request.POST.get("monto_inicial", 0))

        Caja.objects.create(
            negocio=negocio,
            usuario=request.user,
            monto_inicial=monto_inicial,
            estado="abierta",
            fecha_apertura=now(),
        )

        return redirect("/ventas/")

    return render(request, "abrir_caja.html")


@login_required
def cerrar_caja(request):

    negocio = Negocio.objects.filter(usuarios=request.user).first()

    caja = Caja.objects.filter(negocio=negocio, estado="abierta").first()

    if not caja:
        return redirect("/ventas/")

    # 🔥 SOLO ventas de esta caja
    ventas = Venta.objects.filter(caja=caja)

    efectivo = sum(float(v.total) for v in ventas if v.tipo_pago == "efectivo")
    transferencia = sum(
        float(v.total) for v in ventas if v.tipo_pago == "transferencia"
    )

    total_ventas = efectivo + transferencia

    caja.monto_final = float(caja.monto_inicial) + total_ventas
    caja.estado = "cerrada"
    caja.fecha_cierre = now()
    caja.save()

    return render(
        request,
        "cierre_caja.html",
        {
            "caja": caja,
            "efectivo": efectivo,
            "transferencia": transferencia,
            "total": total_ventas,
        },
    )


@login_required
def historial_cajas(request):
    negocio = Negocio.objects.filter(usuarios=request.user).first()

    cajas = Caja.objects.filter(negocio=negocio).order_by("-fecha_apertura")

    return render(request, "historial_cajas.html", {"cajas": cajas})
