#!/usr/bin/env python

from __future__ import print_function

import numpy as np


class Trainer:

    def __init__(self):
        self.x = []
        self.y = []

    def gradient_descent(self, num_iter, alpha, lambd):
        m = self.x.shape[0]
        x = Math.feature_scaling(self.x)
        y = self.y
        theta = np.zeros((x.shape[1],1))
        for i in range(num_iter):
            h = Math.sigmoid(np.einsum('ij,jk', x, theta))
            theta = theta - (alpha/m)*np.einsum('ji,jk', x, (h-y))

            j = (np.einsum('ji,jk', -1*y, np.log(h)) - np.einsum('ji,jk', (1-y), np.log(1-h)))/m
        return theta

    def get_x_y(self):
        return [self.x, self.y]