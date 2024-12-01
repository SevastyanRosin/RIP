from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('units/<int:unit_id>/', unit),
    path('orders/<int:order_id>/', order),
]