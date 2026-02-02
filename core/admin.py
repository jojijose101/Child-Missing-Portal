from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MissingChild as Missing

# Register your models here.
admin.site.register(Missing)
