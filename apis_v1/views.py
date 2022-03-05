from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from .models import Results, InfrenceModels
from django.core.files.base import ContentFile
from .serializers import ResultsSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
import torch
from typing import Optional
import cv2
from PIL import Image
import numpy as np


class Inference:
    def __init__(self):
        self.model = None
        # self.load()    
        
    def load(self):
        pass
        # model = InfrenceModels.objects.latest('id')
        # self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model.file.path, force_reload=True) 

inference_model = Inference()

def results_to_json(results, thresh, img):
    count = 0
    for pred in results.xyxyn[0]:
        if float(pred[4]) > thresh:
            count += 1
  
    for box in results.xyxy[0]: 
        if box[5]==0 and float(box[4]) > thresh:
            xB = int(box[2])
            xA = int(box[0])
            yB = int(box[3])
            yA = int(box[1])
            color = (0, 255, 255)
            thickness = 2
            # img = cv2.rectangle(img, (xA, yA), (xB, yB), (255, 0, 0), 2)
            img = cv2.circle(img, [(xA+xB)//2, (yA+yB)//2], 2, color, thickness)

    #add count to image 
    h,w, c = img.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    img = cv2.putText(img, str(count), (w-200,h-100), font, 4, (255,0,0), 2, cv2.LINE_AA)

    result = Results.objects.create(count=count)
    ret, buf = cv2.imencode('.jpg', img) # cropped_image: cv2 / np array
    content = ContentFile(buf.tobytes())
    # result.image.save('{}.jpg'.format(result.pk), img)
    result.output.save('{}.jpg'.format(result.pk), content)
    return result

   

@api_view(['GET'])
def reload_model(request):
    inference_model.load()
    return Response(status=status.HTTP_200_OK)

from subprocess import Popen, PIPE, STDOUT
import shutil
import os, random, string
def detect(model_path, og_path, file_name, thresh, iou):
    try:
        shutil.rmtree('/home/counter/media/results/exp') # remove old folder
    except FileNotFoundError:
          pass

    cmd = f"/home/venv_counter/bin/python /home/yolov5/detect.py --weights {model_path} --iou-thres {iou} --project /home/counter/media/results --name exp --img 960 --conf-thres {thresh} --save-txt --line-thickness 2 --hide-labels --hide-conf --source {og_path}"
    print(cmd)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = str(p.stdout.read())
    try:
        count = output[output.find('960x960 '):].split(' ')[1]
    except:
        count = 0
    
    exp_path = '/home/counter/media/results/exp/{}'.format(file_name)
    print(exp_path)
    img = cv2.imread(exp_path)
    font = cv2.FONT_HERSHEY_SIMPLEX
    if img is not None:
        h,w, c = img.shape
        img = cv2.putText(img, str(count), (w-300, 100), font, 3, (0,0,255), 2, cv2.LINE_AA)
        cv2.imwrite(exp_path, img)
        os.remove(og_path) # remove old folder
        return count, output
    else:
        return 0, output

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img



def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

@api_view(['POST'])
def inference(request):
    thresh = float(request.GET.get('thresh', 0.5))
    thresh = thresh
    iou = float(request.GET.get('iou', 0.25))
    img = Image.open(request.FILES['image'])
    img = np.array(img) 
    img = cv2.resize(img, (960, 960))
    img = apply_brightness_contrast(img, 35, 5)
    # img = remove_shadow(img)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # bilateral = cv2.bilateralFilter(img, 16, 150, 150)
    # create random string for image name 
    file_name = "img_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=50)) + ".jpg"
    og_path = f'/home/counter/media/' + file_name
    saved = cv2.imwrite(og_path, img)
    print('saved', saved)
    if saved:
        model = InfrenceModels.objects.latest('id')
        count, output = detect(model.file.path, og_path, file_name, thresh, iou)
        url = 'https://api-counter.cruv.dev/media/results/exp/{}'.format(file_name)
    else:
        count = 0
        output = 'error'
        url = 'https://api-counter.com/api/v1/results/tryagain.jpg'
    # results = results_to_json(pred, thresh, img)
    # data = ResultsSerializer(results, context={'request': request}).data
    data = {'count': count, 'thresh': thresh, 'output': url, 'stdout': output}
    return Response(data, status=status.HTTP_202_ACCEPTED)


