# plate_detection/views.py

import cv2
import numpy as np
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import PlateImageForm
from .models import PlateImage
import os
import pytesseract
from PIL import Image

def home(request):
    if request.method == 'POST':
        form = PlateImageForm(request.POST, request.FILES)
        if form.is_valid():
            plate_image = form.save()
            
            # Process the image
            process_image(plate_image)
            
            return redirect('results', pk=plate_image.pk)
    else:
        form = PlateImageForm()
    
    return render(request, 'plate_detection/home.html', {'form': form})

def results(request, pk):
    plate_image = PlateImage.objects.get(pk=pk)
    return render(request, 'plate_detection/results.html', {'plate_image': plate_image})



def process_image(plate_image):
    # Read the uploaded image
    image_path = os.path.join(settings.MEDIA_ROOT, plate_image.image.name)
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply noise reduction
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Edge detection
    edged = cv2.Canny(gray, 170, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    plate_contour = None
    plate = None
    
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        if len(approx) == 4:
            plate_contour = approx
            x, y, w, h = cv2.boundingRect(contour)
            plate = gray[y:y + h, x:x + w]
            
            # Additional processing for better OCR results
            plate = cv2.threshold(plate, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            plate = cv2.medianBlur(plate, 3)
            break
    
    if plate_contour is not None:
        # Draw rectangle around plate
        cv2.drawContours(img, [plate_contour], -1, (0, 255, 0), 3)
        
        # Save processed image
        processed_image_path = os.path.join(settings.MEDIA_ROOT, 'processed_images', os.path.basename(plate_image.image.name))
        cv2.imwrite(processed_image_path, img)
        
        # Perform OCR on the plate
        try:
            # Configure Tesseract (modify based on your country's plate format)
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Convert OpenCV image to PIL format
            plate_pil = Image.fromarray(plate)
            
            # Perform OCR
            # Set the Tesseract path (Windows specific)
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            plate_text = pytesseract.image_to_string(plate_pil, config=custom_config)
            plate_text = ''.join(e for e in plate_text if e.isalnum())  # Clean special characters
            
            # Save results
            plate_image.processed_image = 'processed_images/' + os.path.basename(plate_image.image.name)
            plate_image.detected_plate = plate_text if plate_text else "No plate detected"
        except Exception as e:
            plate_image.detected_plate = f"OCR Error: {str(e)}"
        
        plate_image.save()

# def process_image(plate_image):
#     # Read the uploaded image
#     image_path = os.path.join(settings.MEDIA_ROOT, plate_image.image.name)
#     img = cv2.imread(image_path)
    
#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # Apply bilateral filter to reduce noise while keeping edges sharp
#     gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
#     # Find edges in the image
#     edged = cv2.Canny(gray, 170, 200)
    
#     # Find contours based on edges
#     contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
#     # Sort contours based on area and keep top 10
#     contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
#     plate_contour = None
#     plate = None
    
#     # Loop over contours to find the best rectangular contour
#     for contour in contours:
#         perimeter = cv2.arcLength(contour, True)
#         approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
#         # If the approximated contour has 4 points, it might be a rectangle
#         if len(approx) == 4:
#             plate_contour = approx
#             x, y, w, h = cv2.boundingRect(contour)
#             plate = gray[y:y + h, x:x + w]
#             break
    
#     if plate_contour is not None:
#         # Draw rectangle around the plate
#         cv2.drawContours(img, [plate_contour], -1, (0, 255, 0), 3)
        
#         # Save the processed image
#         processed_image_path = os.path.join(settings.MEDIA_ROOT, 'processed_images', os.path.basename(plate_image.image.name))
#         cv2.imwrite(processed_image_path, img)
        
#         # Update the model with processed image
#         plate_image.processed_image = 'processed_images/' + os.path.basename(plate_image.image.name)
        
#         # For demo purposes, we'll just set a dummy plate number
#         # In a real application, you would use OCR here (like Tesseract)
#         plate_image.detected_plate = "DEMO-1234"
#         plate_image.save()