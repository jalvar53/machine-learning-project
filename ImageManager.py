from skimage.segmentation import slic
import ImageStat
import ImageManager
import numpy
import sys
import cv2
import os


def load_image(img_title):
    path = 'assets/raw/frame'+img_title+'.jpg'
    img = cv2.imread(path, -1)
    cv2.imshow("Image", img)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return img


def slice_image(self, img, rows, columns):
    height, width, channels = img.shape
    height = height / rows
    width = width / columns
    size = (rows, columns, height, width, channels)
    parts = numpy.zeros(size)

    for i in range(0, rows):

        for j in range(0, columns):

            parts[i, j] = img[i * height:(i + 1) * height, j * width:(j + 1) * width]

    return parts


def slic_image(img, parts):
    segments = slic(img, n_segments=parts, sigma=5)
    return segments


def normalized_means(img):
    B, G, R = cv2.split(img)
    R = numpy.mean(R / (R + G + B))
    G = numpy.mean(G / (R + G + B))
    B = numpy.mean(B / (R + G + B))
    return [R, G, B]


def calculate_means(img):
    B, G, R = cv2.split(img)
    R = numpy.mean(R)
    G = numpy.mean(G)
    B = numpy.mean(B)
    return [R, G, B]


def calculate_means2(img):
    R = img[:, 0]
    G = img[:, 1]
    B = img[:, 2]
    R = numpy.mean(R)
    G = numpy.mean(G)
    B = numpy.mean(B)
    return [R, G, B]


def entropy(img):
    cv2.imwrite('temp.jpg', img)

    try:
        img = 'aux.jpg'
        img = ImageManager.load_image(img)
        stat = ImageStat.Stat(img)
        noise = 0
        for i in [float(elem) / stat.count[0] for elem in stat.h]:
            if i != 0:
                noise += i * cv2.log(1. / i, 2)

    except StandardError:
        print("Unexpected error: ", sys.exc_info()[0])

    os.remove('aux.jpg')

    if noise == 0:
        noise = 1e-310
    return noise
