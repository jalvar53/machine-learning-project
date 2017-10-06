#!/usr/bin/env python

from __future__ import print_function
from sklearn.externals import joblib
from sklearn import svm
import ImageManager
import numpy as np
import time


class Trainer:

    def __init__(self):
        self.model = svm.SVC()
        self.x = []
        self.y = []

    def get_x_y(self):
        return [self.x, self.y]

    def train_model(self):
        t = time.time()
        for i in range(10):
            img = ImageManager.load_image('assets/raw/frame000' + str(i) + '.jpg')
            cmp = ImageManager.load_image("assets/mask/frame000"+str(i)+".jpg")
            parts = ImageManager.slice_image(img,9,12)
            for j in range(108):
                means = ImageManager.calculate_means(parts[j])
                self.x.append((means[0], means[1],means[2],ImageManager.entropy(parts[j])))
                if(np.mean(cmp[int(j/12)*53:(int(j/12)+1)*53,j%12*53:((j%12)+ 1)*53,:]) > 130):
                    self.y.append(1)
                else:
                    self.y.append(0)
        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.y = self.y.reshape(self.x.shape[0], 1)
        print(self.x)
        print(self.y)
        print(time.time()-t)
        self.model.fit(self.x, self.y.reshape((self.x.shape[0])))

    def save_model(self):
        joblib.dump(self.model, 'model.pkl')


if __name__ == '__main__':
    trainer = Trainer()
    trainer.train_model()
    trainer.save_model()
