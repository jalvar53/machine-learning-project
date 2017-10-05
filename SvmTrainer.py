#!/usr/bin/env python

from __future__ import print_function
from sklearn.externals import joblib
from sklearn import svm
import ImageManager


class Trainer:

    def __init__(self):
        self.x = []
        self.y = []
        self.model

    def trainModel(self):
        self.model = svm.SVC()

    def get_x_y(self):
        return [self.x, self.y]

    def train_model(self):
        model = svm.SVC()
        model.fit(self.x, self.y.reshape((self.x.shape[0])))

    def save_model(self):
        joblib.dump(self.model, 'model.pkl')


if __name__ == '__main__':
    img = ImageManager.load_image("frame0000")
    segments = ImageManager.slice_image(img, 5, 5);

