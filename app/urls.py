from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('units/<int:unit_id>/', unit_details, name="unit_details"),
    path('units/<int:unit_id>/add_to_order/', add_unit_to_draft_order, name="add_unit_to_draft_order"),
    path('orders/<int:order_id>/delete/', delete_order, name="delete_order"),
    path('orders/<int:order_id>/', order)
]
