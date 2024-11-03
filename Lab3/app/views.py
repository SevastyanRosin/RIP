from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .serializers import *


def get_draft_order():
    return Order.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_units(request):
    unit_name = request.GET.get("unit_name", "")

    units = Unit.objects.filter(status=1)

    if unit_name:
        units = units.filter(name__icontains=unit_name)

    serializer = UnitsSerializer(units, many=True)
    
    draft_order = get_draft_order()

    resp = {
        "units": serializer.data,
        "units_count": UnitOrder.objects.filter(order=draft_order).count() if draft_order else None,
        "draft_order": draft_order.pk if draft_order else None
    }

    return Response(resp)


@api_view(["GET"])
def get_unit_by_id(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit)

    return Response(serializer.data)


@api_view(["PUT"])
def update_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    serializer = UnitSerializer(unit, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_unit(request):
    serializer = UnitSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Unit.objects.create(**serializer.validated_data)

    units = Unit.objects.filter(status=1)
    serializer = UnitSerializer(units, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    unit.status = 2
    unit.save()

    units = Unit.objects.filter(status=1)
    serializer = UnitSerializer(units, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_unit_to_order(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    draft_order = get_draft_order()

    if draft_order is None:
        draft_order = Order.objects.create()
        draft_order.owner = get_user()
        draft_order.date_created = timezone.now()
        draft_order.save()

    if UnitOrder.objects.filter(order=draft_order, unit=unit).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = UnitOrder.objects.create()
    item.order = draft_order
    item.unit = unit
    item.save()

    serializer = OrderSerializer(draft_order)
    return Response(serializer.data["units"])


@api_view(["POST"])
def update_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    image = request.data.get("image")
    if image is not None:
        unit.image = image
        unit.save()

    serializer = UnitSerializer(unit)

    return Response(serializer.data)


@api_view(["GET"])
def search_orders(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    orders = Order.objects.exclude(status__in=[1, 5])

    if status > 0:
        orders = orders.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        orders = orders.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        orders = orders.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = OrdersSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_order_by_id(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 2
    order.date_formation = timezone.now()
    order.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order = Order.objects.get(pk=order_id)

    if order.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        order.date = calc()

    order.date_complete = timezone.now()
    order.status = request_status
    order.moderator = get_moderator()
    order.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 5
    order.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_unit_from_order(request, order_id, unit_id):
    if not UnitOrder.objects.filter(order_id=order_id, unit_id=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = UnitOrder.objects.get(order_id=order_id, unit_id=unit_id)
    item.delete()

    items = UnitOrder.objects.filter(order_id=order_id)
    data = [UnitItemSerializer(item.unit, context={"value": item.value}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_unit_in_order(request, order_id, unit_id):
    if not UnitOrder.objects.filter(unit_id=unit_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = UnitOrder.objects.get(unit_id=unit_id, order_id=order_id)

    serializer = UnitOrderSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)