import os 
import uuid

from rest_framework.decorators import api_view
from .models import InfrenceModels
from rest_framework.response import Response
from rest_framework import status

from yolov5.detect_custom import detection 
from .image_utils import ImageUtils
import cv2

image_utils = ImageUtils()

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(base_dir)


import os
import time

@api_view(['POST'])
def inference(request):
    domain = request.META['HTTP_HOST']
    thresh = float(request.GET.get('thresh', 0.5))
    iou = float(request.GET.get('iou', 0.25))
    img = image_utils.enhance(request.FILES['image'])

    uid = uuid.uuid4().hex
    file_name = uid + ".jpg"
    og_path = os.path.join(base_dir, 'media', file_name) 
    cv2.imwrite(og_path, img)
    results, coords = detection(og_path, thresh, iou)
    img= image_utils.add_results_to_img(coords, img)
    cv2.imwrite(og_path, img)
    data = {'count': len(results), 'thresh': thresh, 'output' : f"http://{domain}/media/{file_name}"}


    # remove files created 5 minutes ago
    for f in os.listdir(os.path.join(base_dir, 'media')):
        if os.path.isfile(os.path.join(base_dir, 'media', f)):
            if os.stat(os.path.join(base_dir, 'media', f)).st_ctime < (time.time() - 60):
                os.remove(os.path.join(base_dir, 'media', f))
    return Response(data, status=status.HTTP_202_ACCEPTED)


