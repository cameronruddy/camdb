import numpy as np
from PIL import Image as im

import cv2
from cv_bridge import CvBridge, CvBridgeError

class make_img:
    bridge = CvBridge()

    def __init__(self):
        pass
        
    def make_image(self, image_raw, path):
        #image_raw = np.frombuffer(msg.data, dtype=np.uint8).reshape(
        #    msg.height, msg.width, -1)
        
        image_RGB = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)

        image_out = im.fromarray(image_RGB)
        
        image_out.save(path + '.png')
        return True # TODO: Does SAVE return a value?
        
    def from_raw(self, msg, path):
        image_raw = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, -1)
        return self.make_image(image_raw, path)

    def decompress(self, msg, path):
        image_raw = np.frombuffer(msg.data, dtype=np.uint8)
        image_decode = cv2.imdecode(image_raw, cv2.IMREAD_COLOR)
        return self.make_image(image_decode, path)
        
   


    


        
