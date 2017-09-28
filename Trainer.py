#!/usr/bin/env python

from __future__ import print_function
import time
import rospy
import Image as Img
import ImageStat
import os
from math import log
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from matplotlib import pyplot as plt
from sensor_msgs.msg import Image

class Trainer:

    def __init__(self):
        self.image_received = False
        self.colores = {}
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.convertToCVFormat)
        rospy.sleep(1)

    def moverse(self, pub):
        msg = Twist()
        r = rospy.Rate(10)
        msg.linear.x = 0.2
        msg.linear.y =0.2
        msg.angular.z= 0
        tini = time.time()

        while time.time()-tini < 5:
            pub.publish(msg)
            r.sleep()

    def obtener_datos(self):
        vis = np.zeros(self.image.shape[:2], dtype="float")
        pixels = slic(self.image, n_segments = 100, sigma = 5)
        self.y = []
        #cont =0
        self.x = []
        for v in np.unique(pixels):
            R=self.image[:,:,0]
            G=self.image[:,:,1]
            B=self.image[:,:,2]
            R= R[pixels==v]
            G= G[pixels==v]
            B= B[pixels==v]
            img = np.dstack((R,G,B))
            medias = self.medias(img)
            mediasn = self.mediasNormalizadas(img)
            self.x.append((medias[0],medias[1],medias[2],self.entropia(img)))
            img = self.masked_image[pixels==v]
            medias=np.mean(img)
            if(np.mean(medias)>127):
                self.y.append(1)
                vis[pixels==v]=1
            else:
                self.y.append(0)
                vis[pixels==v]=0

        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.y = self.y.reshape(self.x.shape[0],1)
        plt.subplot(121), plt.imshow(mark_boundaries(self.image, pixels))
        plt.subplot(122), plt.imshow(vis)
        plt.show()

    def gradiente_descendiente(self,numIter,alpha,lambd):
        m = self.x.shape[0]
        x=feature_scaling(self.x)
        y=self.y
        theta = np.zeros((x.shape[1],1))
        for i in range(numIter):
            h = sigmoid(np.einsum('ij,jk',x,theta))
            theta = theta - (alpha/m)*np.einsum('ji,jk',x,(h-y))

            j = (np.einsum('ji,jk',-1*y,np.log(h)) - np.einsum('ji,jk',(1-y),np.log(1-h)))/m
        return theta

    def get_x_y(self):
        return [self.x, self.y]