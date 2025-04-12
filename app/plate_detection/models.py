# plate_detection/models.py

from django.db import models

class PlateImage(models.Model):
    image = models.ImageField(upload_to='plate_images/')
    detected_plate = models.CharField(max_length=20, blank=True)
    processed_image = models.ImageField(upload_to='processed_images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plate detection {self.id}"