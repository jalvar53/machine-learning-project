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
        #self.image = []
        self.image_received = False
        rospy.sleep(1)

    def refresh_image(self):
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.convert_to_cv_format)

    def convert_to_cv_format(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def move_around(self,pub):
        msg = Twist()
        msg.linear.x = 0
        msg.angular.z= 0.1
        pub.publish(msg)
        print("move_around")

    def move(self, pub, p):
        msg = Twist()
        # r = rospy.Rate(10)
        # msg.linear.x = 1
        # msg.linear.y = 2
        # msg.angular.z = 0
        # tini = time.time()
        if(p[88]==1 and p[89]==1 and p[90]==1 and p[91]==1):
            msg.linear.x = 1
            msg.angular.z= 0
        elif(p[104]==1 and p[105]==1):
            msg.linear.x = 0
            msg.angular.z= -1
        else:
            msg.linear.x = 0
            msg.angular.z= 1
        pub.publish(msg)

        # while time.time() - tini < 5:
        #     pub.publish(msg)
        #     r.sleep()

    def retrieve_data(self):
        self.trainer.x = []
        self.trainer.y = []
        vis = np.zeros(self.image.shape[:2], dtype="float")
        pixels = slic(self.image, n_segments=100, sigma=5)

        #t=time.time()
        #cont =0
        for v in np.unique(pixels):
            #t=time.time()
            img = self.image[pixels==v]
            #print(img.shape)
            #print("tiempo proceso 0: %f" %(time.time()-t))
            #t = time.time()
            means = self.calculate_means2(img)
            #if(cont < 10):
            #print("tiempo de medias: %f" %(time.time()-tini))
            #meansn = self.normalized_means(img)
            self.trainer.x.append((means[0], means[1], means[2], self.entropy(img)))
            #print("tiempo proceso 1: %f" %(time.time()-t))
            #t = time.time()
            img = self.masked_image[pixels == v]
            #means = np.mean(img)
            #print(np.mean(img))
            #print("tiempo proceso 2: %f" %(time.time()-t))
            #t = time.time()
            # if np.mean(means) > 127:
            #     self.trainer.y.append(1)
            #     #vis[pixels == v] = 1
            # else:
            #     self.trainer.y.append(0)
            #     #vis[pixels == v] = 0
            if np.mean(img) > 130:
                self.trainer.y.append(1)
                #vis[pixels == v] = 1
            else:
                self.trainer.y.append(0)
                #vis[pixels == v] = 0
            #cont = cont + 1
            #print("tiempo proceso 3: %f" %(time.time()-t))
        #print("tiempo proceso completo: %f" %(time.time()-t))
        #print(cont)
        self.trainer.x = np.asarray(self.trainer.x)
        self.trainer.y = np.asarray(self.trainer.y)
        self.trainer.y = self.trainer.y.reshape(self.trainer.x.shape[0], 1)
        #plt.subplot(131), plt.imshow(mark_boundaries(self.image, pixels))
        #plt.subplot(132), plt.imshow(vis)
        #plt.subplot(133) , plt.imshow(mark_boundaries(((self.image[:, :, 0] <= 155)*255.0), pixels))
        #plt.subplot(133) , plt.imshow(mark_boundaries(vis, pixels))

        #plt.imshow(mark_boundaries(((self.image[:, :, 0] == 155)*255.0, pixels))
        #plt.show()

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

    def calculate_means2(self, img):
        R = img[:, 0]
        G = img[:, 1]
        B = img[:, 2]
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
        #os.remove('aux.jpg')
        if h == 0:
            h = 1e-310
        return h
