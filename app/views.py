import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_order(request):
    user = identity_user(request)

    if user is None:
        return None

    order = Order.objects.filter(owner=user).filter(status=1).first()

    return order


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_units(request):
    unit_name = request.GET.get("unit_name", "")

    units = Unit.objects.filter(status=1)

    if unit_name:
        units = units.filter(name__icontains=unit_name)

    serializer = UnitsSerializer(units, many=True)

    draft_order = get_draft_order(request)

    resp = {
        "units": serializer.data,
        "units_count": UnitOrder.objects.filter(order=draft_order).count() if draft_order else None,
        "draft_order_id": draft_order.pk if draft_order else None
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
@permission_classes([IsModerator])
def update_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    serializer = UnitSerializer(unit, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_unit(request):
    serializer = UnitSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Unit.objects.create(**serializer.validated_data)

    units = Unit.objects.filter(status=1)
    serializer = UnitSerializer(units, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    unit.status = 2
    unit.save()

    unit = Unit.objects.filter(status=1)
    serializer = UnitSerializer(unit, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_unit_to_order(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    draft_order = get_draft_order(request)

    if draft_order is None:
        draft_order = Order.objects.create()
        draft_order.date_created = timezone.now()
        draft_order.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    unit.image = image
    unit.save()

    serializer = UnitSerializer(unit)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_orders(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    orders = Order.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        orders = orders.filter(owner=user)

    if status_id > 0:
        orders = orders.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        orders = orders.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        orders = orders.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = OrdersSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_by_id(request, order_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=OrderSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order(request, order_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, order_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 2
    order.date_formation = timezone.now()
    order.save()

    serializer = OrderSerializer(order)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
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

    order.status = request_status
    order.date_complete = timezone.now()
    order.moderator = identity_user(request)
    order.save()

    serializer = OrderSerializer(order)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_order(request, order_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 5
    order.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_unit_from_order(request, order_id, unit_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not UnitOrder.objects.filter(order_id=order_id, unit_id=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = UnitOrder.objects.get(order_id=order_id, unit_id=unit_id)
    item.delete()

    order = Order.objects.get(pk=order_id)

    serializer = OrderSerializer(order)
    units = serializer.data["units"]

    return Response(units)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_unit_order(request, order_id, unit_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not UnitOrder.objects.filter(unit_id=unit_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = UnitOrder.objects.get(unit_id=unit_id, order_id=order_id)

    serializer = UnitOrderSerializer(item)

    return Response(serializer.data)


@swagger_auto_schema(method='PUT', request_body=UnitOrderSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_unit_in_order(request, order_id, unit_id):
    user = identity_user(request)

    if not Order.objects.filter(pk=order_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not UnitOrder.objects.filter(unit_id=unit_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = UnitOrder.objects.get(unit_id=unit_id, order_id=order_id)

    serializer = UnitOrderSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
