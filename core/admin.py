from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MissingChild as Missing
from . models import Report, StationProfile

# Register your models here.
admin.site.register(Missing)
admin.site.register(Report)
admin.site.register(StationProfile)