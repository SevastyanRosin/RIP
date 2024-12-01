from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/units/', search_units),  # GET
    path('api/units/<int:unit_id>/', get_unit_by_id),  # GET
    path('api/units/<int:unit_id>/update/', update_unit),  # PUT
    path('api/units/<int:unit_id>/update_image/', update_unit_image),  # POST
    path('api/units/<int:unit_id>/delete/', delete_unit),  # DELETE
    path('api/units/create/', create_unit),  # POST
    path('api/units/<int:unit_id>/add_to_order/', add_unit_to_order),  # POST

    # Набор методов для заявок
    path('api/orders/', search_orders),  # GET
    path('api/orders/<int:order_id>/', get_order_by_id),  # GET
    path('api/orders/<int:order_id>/update/', update_order),  # PUT
    path('api/orders/<int:order_id>/update_status_user/', update_status_user),  # PUT
    path('api/orders/<int:order_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/orders/<int:order_id>/delete/', delete_order),  # DELETE

    # Набор методов для м-м
    path('api/orders/<int:order_id>/units/<int:unit_id>/', get_unit_order),  # GET
    path('api/orders/<int:order_id>/update_unit/<int:unit_id>/', update_unit_in_order),  # PUT
    path('api/orders/<int:order_id>/delete_unit/<int:unit_id>/', delete_unit_from_order),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
