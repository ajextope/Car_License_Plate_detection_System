
# plate_detection/admin.py

from django.contrib import admin
from .models import PlateImage

@admin.register(PlateImage)
class PlateImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'detected_plate')
    list_filter = ('created_at',)
    search_fields = ('detected_plate',)
    readonly_fields = ('created_at',)