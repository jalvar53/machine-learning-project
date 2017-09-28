import time
import rospy
import sys
import cv2
import os
import ImageStat
import numpy as np
import Image as Img
from math import log
from geometry_msgs.msg import Twist
from skimage.segmentation import slic
from cv_bridge import CvBridge, CvBridgeError
from skimage.segmentation import mark_boundaries
from matplotlib import pyplot as plt
from sensor_msgs.msg import Image


class Turtlebot:

    def __init__(self, trainer):
        self.trainer = trainer
        self.bridge = CvBridge()
        self.means = []
        self.colors = {}
        self.normalizedMeans = []
        self.masked_image = []
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.convert_to_cv_format)
        self.image = []
        self.image_received = False
        rospy.sleep(1)

    def convert_to_cv_format(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def move(self, pub):
        msg = Twist()
        r = rospy.Rate(10)
        msg.linear.x = 1
        msg.linear.y = 2
        msg.angular.z = 0
        tini = time.time()

        while time.time() - tini < 5:
            pub.publish(msg)
            r.sleep()

    def retrieve_data(self):
        vis = np.zeros(self.image.shape[:2], dtype="float")
        pixels = slic(self.image, n_segments=100, sigma=5)
        for v in np.unique(pixels):
            R = self.image[:, :, 0]
            G = self.image[:, :, 1]
            B = self.image[:, :, 2]
            R = R[pixels == v]
            G = G[pixels == v]
            B = B[pixels == v]
            img = np.dstack((R, G, B))
            means = self.calculate_means(img)
            meansn = self.normalized_means(img)
            self.trainer.x.append((means[0], means[1], means[2], self.entropy(img)))
            img = self.masked_image[pixels == v]
            means = np.mean(img)
            if np.mean(means) > 127:
                self.trainer.y.append(1)
                vis[pixels == v] = 1
            else:
                self.trainer.y.append(0)
                vis[pixels == v] = 0

        self.trainer.x = np.asarray(self.trainer.x)
        self.trainer.y = np.asarray(self.trainer.y)
        self.trainer.y = self.trainer.y.reshape(self.trainer.x.shape[0], 1)
        plt.subplot(121), plt.imshow(mark_boundaries(self.image, pixels))
        plt.subplot(122), plt.imshow(vis)
        plt.show()

    def get_rgb_channels(self):
        red = np.zeros((480, 640, 3), 'uint8')
        green = np.zeros((480, 640, 3), 'uint8')
        blue = np.zeros((480, 640, 3), 'uint8')
        r = self.image[:, :, 0]
        g = self.image[:, :, 1]
        b = self.image[:, :, 2]
        red[:, :, 0] = r
        green[:, :, 1] = g
        blue[:, :, 2] = b
        cv2.imwrite('red.jpg', blue)
        cv2.imwrite('green.jpg', green)
        cv2.imwrite('blue.jpg', red)

    def normalized_means(self, img):
        R = img[:, :, 0]
        G = img[:, :, 1]
        B = img[:, :, 2]
        R = np.mean(R/(R+G+B))
        G = np.mean(G/(R+G+B))
        B = np.mean(B/(R+G+B))
        return [R, G, B]

    def calculate_means(self, img):
        R = img[:, :, 0]
        G = img[:, :, 1]
        B = img[:, :, 2]
        R = np.mean(R)
        G = np.mean(G)
        B = np.mean(B)
        return [R, G, B]

    def entropy(self, img):
        cv2.imwrite('aux.jpg', img)
        try:
            d = 'aux.jpg'
            im = Img.open(d)
            s = ImageStat.Stat(im)
            h = 0
            for i in [float(elem)/s.count[0] for elem in s.h]:
                if i != 0:
                    h += i*log(1./i, 2)
        except:
            print("Unexpected error: ", sys.exc_info()[0])
        os.remove('aux.jpg')
        if h == 0:
            h = 1e-310
        return h
