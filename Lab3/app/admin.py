from django.contrib import admin

from .models import *

admin.site.register(Unit)
admin.site.register(Order)
admin.site.register(UnitOrder)
