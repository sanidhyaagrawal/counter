from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from .models import Results
from django.core.files.base import ContentFile
from .serializers import ResultsSerializer
from rest_framework.response import Response
from rest_framework import status

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
    ret, buf = cv2.imencode('.jpg', img) # cropped_image: cv2 / np array
    orignal_img = ContentFile(buf.tobytes())
    
    for box in results.xyxy[0]: 
        if box[5]==0 and float(box[4]) > thresh:
            xB = int(box[2])
            xA = int(box[0])
            yB = int(box[3])
            yA = int(box[1])
            img = cv2.rectangle(img, (xA, yA), (xB, yB), (255, 0, 0), 2)
    
    ret, buf = cv2.imencode('.jpg', img) # cropped_image: cv2 / np array
    output_img = ContentFile(buf.tobytes())
    
    
    
    result = Results.objects.create(count=count)
    result.image.save('{}.jpg'.format(result.pk), orignal_img)
    result.output.save('{}.jpg'.format(result.pk), output_img)
    return result

   

@api_view(['POST'])
def inference(request):
    thresh = float(request.GET.get('thresh', 0.5))
    img = Image.open(request.FILES['image'])
    img = np.array(img) 
    img = cv2.resize(img, (960, 960))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # bilateral = cv2.bilateralFilter(img, 16, 150, 150)
    result = results_to_json(model(img), thresh, img)
    data = ResultsSerializer(result, context={'request': request}).data
    return Response(data, status=status.HTTP_202_ACCEPTED)


