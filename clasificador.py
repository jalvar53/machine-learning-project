#!/usr/bin/env python

from __future__ import print_function
import sys
import rospy
import cv2
import time
import numpy as np
import Image as Img
import ImageStat
import os
from math import log
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
#from PIL import Image
#from random import randint
from matplotlib import pyplot as plt
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist

#funcion de sigmoid
def sigmoid(z):
    return 1/(1+np.exp(z))

#funcion que me escaal todos lsod atos de 0 a 1
def feature_scaling(x):
    maxs = np.zeros((x.shape[1]))
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if(x[i,j] > maxs[j]):
                maxs[j]=x[i,j]
    for i in range(x.shape[1]):
        x[:,i] = x[:,i]/maxs[i]
    return x

def probabilidad(x,theta):
    return sigmoid(np.einsum('j,jk',x,theta))


class entrenador:
    def __init__(self):

        self.bridge = CvBridge()
        self.image_received = False
        self.colores = {}
        # Connect image topic
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.callback)

        # Allow up to one second to connection
        rospy.sleep(1)

    def callback(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    #funcion que encuentra la tonalidad del piso
    def encontrarValoresPiso(self):
        for j in range(self.image.shape[1]):
            for k in range(self.image.shape[2]):
                if not(int(self.image[self.image.shape[0]-1,j,k]) in self.colores):
                    self.colores[self.image[self.image.shape[0]-1,j,k]] = 1
                else:
                    self.colores[self.image[self.image.shape[0]-1,j,k]] += 1

    #funcion que calcula la imagen de piso y no piso y la guarda
    def guardarImagen(self, img_title):
        if self.image_received:
            mayor = -1
            valorMayorFrecuencia = -1
            for i in self.colores:
                if self.colores[i]>mayor:
                    mayor = self.colores[i]
                    valorMayorFrecuencia = i
            cv2.imwrite(img_title, (self.image[:,:,0]==valorMayorFrecuencia)*255)
            self.masked_image=((self.image[:,:,0]==valorMayorFrecuencia)*255)
            return True
        else:
            return False

    #funcion que permite moverse
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
    #funcion que guarda los tres canales de la imagen en su respectivo nombre.jpg
    def sacarCanales(self):
        red = np.zeros((480,640,3), 'uint8')
        green = np.zeros((480,640,3), 'uint8')
        blue = np.zeros((480,640,3), 'uint8')
        r = self.image[:,:,0]
        g = self.image[:,:,1]
        b = self.image[:,:,2]
        red[:,:,0]=r
        green[:,:,1]=g
        blue[:,:,2]=b
        #plt.subplot(131),plt.imshow(red)
        #plt.subplot(132),plt.imshow(green)
        #plt.subplot(133),plt.imshow(blue)
        #plt.show()
        cv2.imwrite('rojo.jpg', blue)
        cv2.imwrite('verde.jpg', green)
        cv2.imwrite('azul.jpg', red)

    def mediasNormalizadas(self,img):
        R=img[:,:,0]
        G=img[:,:,1]
        B=img[:,:,2]
    	R = np.mean(R/(R+G+B))
    	G = np.mean(G/(R+G+B))
    	B = np.mean(B/(R+G+B))
        return [R,G,B]

    def medias(self, img):
    	R=img[:,:,0]
        G=img[:,:,1]
        B=img[:,:,2]
    	R = np.mean(R)
    	G = np.mean(G)
    	B = np.mean(B)
        return [R,G,B]

    def entropia(self,img):
        cv2.imwrite('aux.jpg',img)
        try:
            d = 'aux.jpg'
            im = Img.open(d)
            s = ImageStat.Stat(im)
            h = 0
            for i in [float(elem)/s.count[0] for elem in s.h]:
                if i != 0 : h += i*log(1./i,2)
        except:
            print("Unexpected error:", sys.exc_info()[0])
        os.remove('aux.jpg')
        if(h==0):
            h=1e-310
        return h

    #funcion que calcula los superpixeles, la matriz x y la matriz y
    def obtener_datos(self):
        vis = np.zeros(self.image.shape[:2], dtype="float")
        pixels = slic(self.image, n_segments = 100, sigma = 5)
        self.y = []
        #cont =0
        self.x = []
        for v in np.unique(pixels):
            #mask = np.ones(self.image.shape[:2])
            #mask[pixels == v] = 0
            #cont = cont +1
            R=self.image[:,:,0]
            G=self.image[:,:,1]
            B=self.image[:,:,2]
            R= R[pixels==v]
            G= G[pixels==v]
            B= B[pixels==v]
            img = np.dstack((R,G,B))
            medias = self.medias(img)
            mediasn = self.mediasNormalizadas(img)
            #print("medias: %f %f %f"%(medias[0],medias[1],medias[2]))
            #print("medias normalizadas: %f %f %f"%(mediasn[0],mediasn[1],mediasn[2]))
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
        #plt.subplot(122), plt.imshow(self.masked_image)
        plt.subplot(122), plt.imshow(vis)
        plt.show()

    #gradiente descendiente para regresion logistica
    def gradiente_descendiente(self,numIter,alpha,lambd):
        m = self.x.shape[0]
        x=feature_scaling(self.x)
        y=self.y
        #theta = np.random.randint(0,10,(x.shape[1],1))
        theta = np.zeros((x.shape[1],1))
        for i in range(numIter):
            h = sigmoid(np.einsum('ij,jk',x,theta))
            #theta = theta*(1-(alpha*lambd)/m) - (alpha/m)*np.einsum('ji,jk',x,(h-y))
            theta = theta - (alpha/m)*np.einsum('ji,jk',x,(h-y))

            j = (np.einsum('ji,jk',-1*y,np.log(h)) - np.einsum('ji,jk',(1-y),np.log(1-h)))/m
            #print(j)
        return theta

    def get_x_y(self):
        return [self.x, self.y]


if __name__ == '__main__':
    rospy.init_node('clasificador', anonymous=False)
    entrenador1 = entrenador()
    pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    entrenador1.encontrarValoresPiso()
    # Use '_image_title' parameter from command line
    titulo = rospy.get_param('~image_title', 'imagen.jpg')
    if entrenador1.guardarImagen(titulo):
        rospy.loginfo("imagen guardada " + titulo)
    else:
        rospy.loginfo("No se capturo imagen")
    #entrenador1.sacarCanales()
    entrenador1.obtener_datos()
    x,y=entrenador1.get_x_y()
    #entrenador1.moverse(pub)
    theta = entrenador1.gradiente_descendiente(100,0.01,100)
    h = sigmoid(np.einsum('ij,jk',x,theta))
    maxi=0
    mini=100001
    for i in range(y.shape[0]):
        if(not(y[i]) and h[i]<mini):
            mini =h[i]
        elif(y[i] and h[i]>maxi):
            maxi=h[i]
    #print(np.einsum('ij,jk',x,theta))
    #print(x)
    #print(theta)
    sol = np.zeros((x.shape[0],x.shape[1]+1),'float')
    sol[:,0]=x[:,0]
    sol[:,1]=x[:,1]
    sol[:,2]=x[:,2]
    sol[:,3]=x[:,3]
    sol[:,4]=y.reshape(108)
    print(sol)
    print(h)
    print("maximo: %f minimo: %f" %(maxi,mini))
    print(probabilidad([1,1,1,3.13423863e-300],theta))


rospy.sleep(1)
