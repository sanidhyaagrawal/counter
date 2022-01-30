from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from .models import Results
# Create your views here.
import torch
from typing import Optional
from pydantic import BaseModel, Field
import cv2
from PIL import Image
import numpy as np

model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/v1m.pt')  # local model

def results_to_json(results, thresh, img):
    count = 0
    for pred in results.xyxyn[0]:
        if float(pred[4]) > thresh:
            count += 1
  
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for box in results.xyxy[0]: 
        if box[5]==0 and float(box[4]) > thresh:
            xB = int(box[2])
            xA = int(box[0])
            yB = int(box[3])
            yA = int(box[1])
            img = cv2.rectangle(img, (xA, yA), (xB, yB), (255, 0, 0), 2)
    
    result = Results.objects.create(count=count, img=img)
    return result
   

@api_view(['POST'])
def inference(request):
    thresh = request.GET.get('thresh', 0.5)
    img = Image.open(request.FILES['img'])
    img = np.array(img) 
    img = cv2.resize(img, (960, 960))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # bilateral = cv2.bilateralFilter(img, 16, 150, 150)
    result = results_to_json(model(img), thresh, img)
    return result.to_json()

