#!/usr/bin/env python

from __future__ import print_function

import numpy as np
from sklearn import svm
from Image import Image

class Trainer:

    def __init__(self):
        self.x = []
        self.y = []
        self.model

    def trainModel(self):
        self.model = svm.SVC()

    def get_x_y(self):
        return [self.x, self.y]

if __name__ == '__main__':
    ImgManager = Image()
    ImgManager.loadImage()

