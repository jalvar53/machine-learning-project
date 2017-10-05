import numpy as np
import cv2

class Image:

    def loadImage(self, img_title):
        img = cv2.imread('assets/raw/frame0000.jpg', -1)
        cv2.imshow('la verga',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()