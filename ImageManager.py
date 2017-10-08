from skimage.segmentation import slic
import ImageManager
import ImageStat
import Image
import numpy
import sys
import cv2
import os
from math import log


def load_image(img_title):
    path = img_title + '.jpg'
    print(path)
    img = cv2.imread(path, -1)
    #cv2.imshow("Image" + img_title, img)
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    return img


def slice_image(img, rows, columns):
    height, width, channels = img.shape
    height = height / rows
    width = width / columns
    parts=[]

    for i in range(0, rows):

        for j in range(0, columns):

            parts.append(img[i * height:(i + 1) * height, j * width:(j + 1) * width])

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

def calculate_y(mask,j):
    return numpy.mean(mask[int(j / 12) * 53:(int(j / 12) + 1) * 53, j % 12 * 53:((j % 12) + 1) * 53, :]) > 130


def entropy(img):
    cv2.imwrite('aux.jpg', img)

    try:

        d = 'aux.jpg'
        im = Image.open(d)
        s = ImageStat.Stat(im)
        h = 0
        for i in [float(elem)/s.count[0] for elem in s.h]:
            if i != 0:
                h += i*log(1./i, 2)

    except StandardError:
        print("Unexpected error: ", sys.exc_info()[0])

    os.remove('aux.jpg')

    noise = h

    if noise == 0:
        noise = 1e-310
    return noise