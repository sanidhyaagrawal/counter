# counter-backend

***Yolov5 based object detection model to count <2mm sized gem-stones***

|API|Body|Description|
|-|-|-|
|`POST /v1/inference`|`{image: file, thresh: confidence}`|Get `count`, result `image url`|
|`GET /v1/reload`|`None`|Load latest model|

---


***Input:***             |  ***Output:***
:-------------------------:|:-------------------------:
<img src="https://user-images.githubusercontent.com/48694206/157450493-33744303-df04-4009-a328-84f4dc0ca383.jpg" alt="Input" width="500">  |  <img src="https://user-images.githubusercontent.com/48694206/157450579-592a4892-ba28-46fb-84f4-02296e91d753.jpg" alt="Output" width="500">







