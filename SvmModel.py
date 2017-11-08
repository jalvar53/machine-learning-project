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
            self.x.append(ImageManager.retrieve_data(img))

            img = mask[segments == segment]
            if np.mean(img) > 130:
                self.y.append(1)
            else:
                self.y.append(0)

        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.y = self.y.reshape(self.x.shape[0], 1)
        self.model.fit(self.x, self.y.reshape((self.x.shape[0])))


    def calculate_data(self, parts, parts_hsv, parts_BaW, mask):
        for j in range(len(parts)):
            self.x.append(ImageManager.retrieve_data(parts[j], parts_hsv[j], parts_BaW[j]))
            self.y.append(ImageManager.calculate_y(mask,j))

    def calculate_data2(self, parts, parts_hsv, parts_BaW, mask, img_BaW, segments):
        #for j in range(len(parts)):
        for (j, segVal) in enumerate(np.unique(segments)):
            self.x.append(ImageManager.retrieve_data2(parts[j], parts_hsv[j]))
            self.y.append(ImageManager.calculate_y2(mask, segVal, segments))

    def train_model_slice(self):
        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        #self.y = self.y.reshape(self.x.shape[0], 1)
        self.model.fit(self.x, self.y.reshape((self.x.shape[0])))


    def save_model(self):
        joblib.dump(self.model, 'model.pkl')

    def load_model(self):
        self.model = joblib.load('model.pkl')

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
    for i in range(101):
        img_name = 'assets/raw/frame' + str(int(i/1000))
        mask_name = 'assets/mask/frame' + str(int(i/1000))
        num = i % 1000
        img_name += str(int(num/100))
        mask_name += str(int(num/100))
        num = num % 100
        img_name += str(int(num/10)) + str(int(num%10))
        mask_name += str(int(num/10)) + str(int(num%10))
        image, imageBaW = ImageManager.load_image(img_name)
        mask = ImageManager.load_image(mask_name)[0]
        #segments = ImageManager.slic_image(image, 100)

        ##diciendo imagen en cuadros
        # parts, parts_hsv, parts_BaW = ImageManager.slice_image(image, imageBaW, 9, 12)
        # svm.calculate_data(parts, parts_hsv, parts_BaW, mask)

        ##con superpixeles
        parts, parts_hsv, parts_BaW, segments = ImageManager.slic_image(image, imageBaW, 9, 12)
        svm.calculate_data2(parts, parts_hsv, parts_BaW, mask, imageBaW, segments)
    svm.train_model_slice()
    svm.save_model()
