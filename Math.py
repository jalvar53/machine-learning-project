import numpy as np


def sigmoid(z):
    return 1/(1+np.exp(z))


def feature_scaling(x):
    maxs = np.zeros((x.shape[1]))
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if x[i, j] > maxs[j]:
                maxs[j] = x[i, j]
    for i in range(x.shape[1]):
        x[:, i] = x[:, i]/maxs[i]
    return x


def probability(x, theta):
    return sigmoid(np.einsum('j,jk', x, theta))
