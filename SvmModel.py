#!/usr/bin/env python

from __future__ import print_function
from sklearn.externals import joblib
from sklearn import svm
import numpy as np
import ImageManager


class SvmModel:

    def __init__(self):
        self.model = svm.SVC()
        self.x = []
        self.y = []

    def get_x_y(self):
        return [self.x, self.y]

    def train_model(self, image, mask, segments):
        self.x = []
        self.y = []
        for segment in np.unique(segments):
            img = image[segments == segment]
            means = ImageManager.calculate_means2(img)

            self.x.append((means[0], means[1], means[2], ImageManager.entropy(img)))

            img = mask[segments == segment]
            if np.mean(img) > 130:
                self.y.append(1)
            else:
                self.y.append(0)

        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.y = self.y.reshape(self.x.shape[0], 1)
        self.model.fit(self.x, self.y.reshape((self.x.shape[0])))

    def save_model(self):
        joblib.dump(self.model, 'model.pkl')

    def load_model(self):
        self.model = joblib.load('model.pkl')

    def predict(self, image, segments):

        self.x = []
        for segment in np.unique(segments):
            img = image[segments == segment]
            means = ImageManager.calculate_means2(img)
            self.x.append((means[0], means[1], means[2], ImageManager.entropy(img)))

        self.x = np.asarray(self.x)
        mask = self.model.predict(self.x)
        return mask

if __name__ == '__main__':
    print("Training the model")
    svm = SvmModel()
    for i in range(20):
        if i <= 9:
            img_name = 'assets/raw/frame000' + str(i)
            mask_name = 'assets/mask/frame000' + str(i)
        else:
            img_name = 'assets/raw/frame00' + str(i)
            mask_name = 'assets/mask/frame00' + str(i)
        image = ImageManager.load_image(img_name)
        mask = ImageManager.load_image(mask_name)
        segments = ImageManager.slic_image(image, 100)
        svm.train_model(image, mask, segments)
    svm.save_model()

