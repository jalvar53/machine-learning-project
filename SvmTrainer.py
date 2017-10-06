#!/usr/bin/env python

from __future__ import print_function
from sklearn.externals import joblib
from sklearn import svm
import ImageManager
import numpy as np
import cv2


class Trainer:

    def __init__(self):
        self.model = svm.SVC()
        self.x = []
        self.y = []

    def get_x_y(self):
        return [self.x, self.y]

    def train_model(self):
        for i in range(10):
            img = ImageManager.load_image("000" + str(i))
            cmp = cv2.imread("assets/mask/frame000"+str(i)+".jpg", -1)
            parts = ImageManager.slice_image(img,9,12)
            for j in range(108):
                means = ImageManager.calculate_means(parts[j])
                self.x.append((means[0], means[1],means[2],ImageManager.entropy(parts[j])))
                if(np.mean(cmp[int(j/12)*53:(int(j/12)+1)*53,j%12*53:((j%12)+ 1)*53,:]) > 130):
                    self.y.append(1)
                else:
                    self.y.append(0)
            #print(len(parts))
        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.y = self.y.reshape(self.x.shape[0], 1)
        #print(self.x.shape)
        #print(self.y.shape)
        self.model.fit(self.x, self.y.reshape((self.x.shape[0])))

    def save_model(self):
        joblib.dump(self.model, 'model.pkl')


if __name__ == '__main__':
    #img = ImageManager.load_image("frame0000")
    #segments = ImageManager.slice_image(img, 5, 5)
    trainer = Trainer()
    trainer.train_model()
