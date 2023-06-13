
import cv2
from PIL import Image
import numpy as np

class ImageUtils:

    @staticmethod
    def increase_brightness(img, value=30):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value

        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img

    @staticmethod
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
    
    def enhance(self, image):
        img = Image.open(image)
        img = np.array(img) 
        img = cv2.resize(img, (960, 960))
        img = self.apply_brightness_contrast(img, 35, 5)
        # img = remove_shadow(img)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img = cv2.filter2D(img, -1, kernel)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # bilateral = cv2.bilateralFilter(img, 16, 150, 150)

        return img
        
    def add_results_to_img(self, coords, img):  
        for box in coords: 
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
        count = len(coords)
        img = cv2.putText(img, str(count), (w-300, 100), font, 3, (0,0,255), 2, cv2.LINE_AA)
        return img
    
      