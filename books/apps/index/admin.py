from django.contrib import admin
from .models import Categories
from django.contrib.auth.models import Permission

admin.site.register(Categories)
admin.site.register(Permission)