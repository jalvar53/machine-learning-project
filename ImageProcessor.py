import sys
import cv2
import os
import ImageStat
import numpy as np
import Image as Img
from math import log


class ImageProcessor:

    def __init__(self, turtlebot):
        self.turtlebot = turtlebot

    def find_floor_values(self):
        for j in range(self.turtlebot.image.shape[1]):
            for k in range(self.turtlebot.image.shape[2]):
                if not(int(self.turtlebot.image[self.turtlebot.image.shape[0]-1, j, k]) in self.turtlebot.colors):
                    self.turtlebot.colors[self.turtlebot.image[self.turtlebot.image.shape[0]-1, j, k]] = 1
                else:
                    self.turtlebot.colors[self.turtlebot.image[self.turtlebot.image.shape[0]-1, j, k]] += 1

    def save_image(self, img_title):
        if self.turtlebot.image_received:
            bigger = -1
            bigger_frequency = -1
            for i in self.turtlebot.colors:
                if self.turtlebot.colors[i] > bigger:
                    bigger = self.turtlebot.colors[i]
                    bigger_frequency = i
            cv2.imwrite(img_title, (self.turtlebot.image[:, :, 0] == bigger_frequency)*255)
            self.turtlebot.masked_image = ((self.turtlebot.image[:, :, 0] == bigger_frequency)*255)
            print(bigger_frequency)
            #plt.imshow(mark_boundaries(self.masked_image, pixels))
            #plt.show()
            return True
        else:
            return False
