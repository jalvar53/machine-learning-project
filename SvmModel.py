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


    def train_model_slic(self, image, mask, segments):
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


    def calculate_data(self, parts, mask):
        for j in range(len(parts)):

            means = ImageManager.calculate_means(parts[j])
            self.x.append((means[0], means[1], means[2], ImageManager.entropy(parts[j])))
            self.y.append(ImageManager.calculate_y(mask,j))

    def train_model_slice(self):
        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        #self.y = self.y.reshape(self.x.shape[0], 1)
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
        msk = self.model.predict(self.x)
        return msk

    def get_x_y(self):
        return [self.x, self.y]

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_model(self):
        return self.model


if __name__ == '__main__':
    print("Training the model")
    svm = SvmModel()
    for i in range(21):
        img_name = 'assets/raw/frame' + str(int(i/1000))
        mask_name = 'assets/mask/frame' + str(int(i/1000))
        num = i%1000
        img_name += str(int(num/100))
        mask_name += str(int(num/100))
        num = num % 100
        img_name += str(int(num/10)) + str(int(num%10))
        mask_name += str(int(num/10)) + str(int(num%10))

        image = ImageManager.load_image(img_name)
        mask = ImageManager.load_image(mask_name)
        #segments = ImageManager.slic_image(image, 100)
        parts = ImageManager.slice_image(image,9,12)
        #svm.train_model_slic(image, mask, segments)
        svm.calculate_data(parts, mask)
    svm.train_model_slice()
    svm.save_model()