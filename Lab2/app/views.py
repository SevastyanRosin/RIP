from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Unit, Order, UnitOrder


def index(request):
    unit_name = request.GET.get("unit_name", "")
    units = Unit.objects.filter(status=1)

    if unit_name:
        units = units.filter(name__icontains=unit_name)

    draft_order = get_draft_order()

    context = {
        "unit_name": unit_name,
        "units": units
    }

    if draft_order:
        context["units_count"] = len(draft_order.get_units())
        context["draft_order"] = draft_order

    return render(request, "units_page.html", context)


def add_unit_to_draft_order(request, unit_id):
    unit_name = request.POST.get("unit_name")
    redirect_url = f"/?unit_name={unit_name}" if unit_name else "/"

    unit = Unit.objects.get(pk=unit_id)

    draft_order = get_draft_order()

    if draft_order is None:
        draft_order = Order.objects.create()
        draft_order.owner = get_current_user()
        draft_order.date_created = timezone.now()
        draft_order.save()

    if UnitOrder.objects.filter(order=draft_order, unit=unit).exists():
        return redirect(redirect_url)

    item = UnitOrder(
        order=draft_order,
        unit=unit
    )
    item.save()

    return redirect(redirect_url)


def unit_details(request, unit_id):
    context = {
        "unit": Unit.objects.get(id=unit_id)
    }

    return render(request, "unit_page.html", context)


def delete_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE orders SET status=5 WHERE id = %s", [order_id])

    return redirect("/")


def order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return redirect("/")

    order = Order.objects.get(id=order_id)
    if order.status == 5:
        return redirect("/")

    context = {
        "order": order,
    }

    return render(request, "order_page.html", context)


def get_draft_order():
    return Order.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()