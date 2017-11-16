from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
import ImageManager
import ImageStat
import Image
import numpy as np
import sys
import cv2
import os
import time
from math import log


def load_image(img_title):
    path = img_title + '.jpg'
    print("\n" + path)
    img = cv2.imread(path, -1)
    imgBaW = cv2.imread(path, 0)
    #cv2.imshow("Image" + img_title, img)
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    return [img, imgBaW]

def retrieve_data(img, img_hsv, img_BaW):
    #means = ImageManager.calculate_means(img)
    #devs = ImageManager.calculate_deviation(img)
    #ranges = ImageManager.calculate_range(img)
    means_hsv = ImageManager.calculate_means(img_hsv)
    devs_hsv = ImageManager.calculate_deviation2(img_hsv)
    ranges_hsv = ImageManager.calculate_range2(img_hsv)
    gradient = cv2.Sobel(img_BaW, cv2.CV_64F,1,0,ksize=-1)
    #print(abs(np.mean(gradient)/250))
    return (#means[0], means[1], means[2], devs[0], devs[1], devs[2], ranges[0], ranges[1], ranges[2],
            means_hsv[0], means_hsv[1], means_hsv[2], devs_hsv[0], devs_hsv[1], devs_hsv[2], ranges_hsv[0], ranges_hsv[1], ranges_hsv[2],
            abs(np.mean(gradient)/250), ImageManager.entropy(img))

def retrieve_data2(img, img_hsv, img_BaW):
    #means = ImageManager.calculate_means(img)
    #devs = ImageManager.calculate_deviation2(img)
    #ranges = ImageManager.calculate_range2(img)
    means_hsv = ImageManager.calculate_means(img_hsv)
    devs_hsv = ImageManager.calculate_deviation2(img_hsv)
    ranges_hsv = ImageManager.calculate_range2(img_hsv)
    #gradient = cv2.Sobel(img_BaW, cv2.CV_64F,1,0,ksize=-1)
    # return (means[0], means[1], means[2], devs[0], devs[1], devs[2], ranges[0], ranges[1], ranges[2],
    #         means_hsv[0], means_hsv[1], means_hsv[2], devs_hsv[0], devs_hsv[1], devs_hsv[2], ranges_hsv[0], ranges_hsv[1], ranges_hsv[2],
    #         abs(np.max(gradient)/13000), ImageManager.entropy(img))
    return (means_hsv[0], means_hsv[1], means_hsv[2], devs_hsv[0], devs_hsv[1], devs_hsv[2], ranges_hsv[0], ranges_hsv[1], ranges_hsv[2],
            #abs(np.max(gradient)/13000),
            ImageManager.entropy(img))

def slice_image(img, img_BaW, rows, columns):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width, channels = img.shape
    height = height / rows
    width = width / columns
    parts=[]
    parts_hsv=[]
    parts_BaW = []
    for i in range(0, rows):

        for j in range(0, columns):

            parts.append(img[i * height:(i + 1) * height, j * width:(j + 1) * width])
            parts_hsv.append(img_hsv[i * height:(i + 1) * height, j * width:(j + 1) * width])
            parts_BaW.append(img_BaW[i * height:(i + 1) * height, j * width:(j + 1) * width])

    return [parts, parts_hsv, parts_BaW]


def slic_image(img, img_BaW, rows, columns):
    #t = time.time()
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #print("tiempo para pasar a hsv: %f" % (time.time()-t))
    #t = time.time()
    n = rows*columns
    segments = slic(img, n_segments=100, sigma=1)
    #print("tiempo para sacar superpixels: %f" % (time.time()-t))
    #t = time.time()
    parts = range(n)
    parts_hsv = range(n)
    parts_BaW = range(n)
    for (i, segVal) in enumerate(np.unique(segments)):
        pos = segments==segVal
        parts[i]=img[pos]
        parts_hsv[i]=img_hsv[pos]
        temp = np.zeros(img_BaW.shape)
        temp[pos] = img_BaW[pos]
        parts_BaW[i]=temp
    #print("tiempo para sacar partes: %f" % (time.time()-t))
    cv2.namedWindow("superpixels");
    cv2.moveWindow("superpixels", 20,20);
    cv2.imshow("superpixels", mark_boundaries(img,segments))
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    return [parts, parts_hsv, parts_BaW, segments]


def normalized_means(img):
    B, G, R = cv2.split(img)
    R = np.mean(R / (R + G + B))
    G = np.mean(G / (R + G + B))
    B = np.mean(B / (R + G + B))
    return [R, G, B]


# def calculate_means(img):
#     B, G, R = cv2.split(img)
#     R = np.mean(R)
#     G = np.mean(G)
#     B = np.mean(B)
#     return [R, G, B]

def calculate_variance(img):
    B, G, R = cv2.split(img)
    R = np.var(R)/2000
    G = np.var(G)/2000
    B = np.var(B)/2000
    return [R, G, B]

def calculate_variance2(img):
    R = img[:, 0]
    G = img[:, 1]
    B = img[:, 2]
    R = np.var(R)/2000
    G = np.var(G)/2000
    B = np.var(B)/2000
    return [R, G, B]

def calculate_range(img):
    Bi, Gi, Ri = cv2.split(img)
    R = (Ri.max() - Ri.min())/255.0
    G = (Gi.max() - Gi.min())/255.0
    B = (Bi.max() - Bi.min())/255.0
    return [R,G,B]

def calculate_range2(img):
    Ri = img[:, 0]
    Gi = img[:, 1]
    Bi = img[:, 2]
    R = (Ri.max() - Ri.min())/255.0
    G = (Gi.max() - Gi.min())/255.0
    B = (Bi.max() - Bi.min())/255.0
    return [R,G,B]

def calculate_deviation(img):
    Bi, Gi, Ri = cv2.split(img)
    R = np.std(Ri)
    G = np.std(Gi)
    B = np.std(Bi)
    if(R.max() > 1):
        R = R/Ri.max()
    if(G.max() > 1):
        G = G/Gi.max()
    if(B.max() > 1):
        B = B/Bi.max()
    return [R, G, B]

def calculate_deviation2(img):
    Ri = img[:, 0]
    Gi = img[:, 1]
    Bi = img[:, 2]
    R = np.std(Ri)
    G = np.std(Gi)
    B = np.std(Bi)
    if(R.max() > 1):
        R = R/Ri.max()
    if(G.max() > 1):
        G = G/Gi.max()
    if(B.max() > 1):
        B = B/Bi.max()
    return [R, G, B]

def calculate_means(img):
    R = img[:, 0]
    G = img[:, 1]
    B = img[:, 2]
    R = np.mean(R)/127
    G = np.mean(G)/127
    B = np.mean(B)/127
    return [R, G, B]

def calculate_y(mask,j):
    return np.mean(mask[int(j / 12) * 53:(int(j / 12) + 1) * 53, j % 12 * 53:((j % 12) + 1) * 53, :]) > 130

def calculate_y2(mask,segVal, segments):
    return np.mean(mask[segVal==segments]) > 127


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
    return noise/20
