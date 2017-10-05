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


def cost1(z):
    sol = np.zeros(z.shape)
    for i in range(sol.shape[0]):
        for j in range(sol.shape[1]):
            if z[i, j] >= 1:
                sol[i, j] = 0
            else:
                sol[i, j] = -1*np.log(1/(1+np.exp(-1*z[i, j])))
    return sol


def cost0(z):
    sol = np.zeros(z.shape)
    for i in range(sol.shape[0]):
        for j in range(sol.shape[1]):
            if z[i, j] <= -1:
                sol[i, j] = 0
            else:
                sol[i, j] = -1*np.log(1-(1/(1+np.exp(-1*z[i, j]))))
    return sol


def similarity(x1, x2):
    f = np.exp(-1*(np.linalg.norm(x1-x2)**2)/2*1**2)
    return f


def svm(self):
    x=feature_scaling(self.x)
    f = np.ones((self.x.shape[0],self.x.shape[0]+1), 'double')
    theta = np.ones((self.x.shape[0],self.x.shape[0]+1), 'double')
    y = self.y
    c = 1
    cont=0
    for i in range(f.shape[0]):
        for j in range(f.shape[1]-1):
            f[i, j+1] = similarity(x[i, :], x[j, :])

    j = c*np.sum((np.einsum('ji,jk', y, cost1(np.einsum('ij,kj', f, theta))) + np.einsum('ji,jk', (1-y), cost0(np.einsum('ij,kj',f,theta))))) + (1/2)*np.sum(np.einsum('ji,jk', theta, theta)) - np.sum(np.einsum('j,j', np.transpose(theta[:, 0]), theta[:, 0]))
    return theta