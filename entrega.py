#!/usr/bin/env python

from __future__ import print_function
import sys
import rospy
import cv2
import time
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist

class infoCamara:
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

    def encontrarValoresPiso(self):
        for j in range(self.image.shape[1]):
            for k in range(self.image.shape[2]):
                if not(int(self.image[self.image.shape[0]-1,j,k]) in self.colores):
                    self.colores[self.image[self.image.shape[0]-1,j,k]] = 1
                else:
                    self.colores[self.image[self.image.shape[0]-1,j,k]] += 1

    def guardarImagen(self, img_title):
        if self.image_received:
            mayor = -1
            valorMayorFrecuencia = -1
            for i in self.colores:
                if self.colores[i]>mayor:
                    mayor = self.colores[i]
                    valorMayorFrecuencia = i
            cv2.imwrite(img_title, (self.image==valorMayorFrecuencia)*255)
            return True
        else:
            return False

    

    def moverseAdelante(self, pub):
        msg = Twist()
        r = rospy.Rate(10)
        msg.linear.x = 0.2
        msg.linear.y =0.2
        msg.angular.z= 0
        tini = time.time()
        
        while time.time()-tini < 5:
            pub.publish(msg)
            r.sleep()

if __name__ == '__main__':
    rospy.init_node('entrega', anonymous=False)
    camara = infoCamara()
    pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    camara.encontrarValoresPiso()
    # Use '_image_title' parameter from command line
    titulo = rospy.get_param('~image_title', 'imagen.jpg')
    #camara.moverseAdelante(pub)
    if camara.guardarImagen(titulo):
        rospy.loginfo("imagen guardada " + titulo)
    else:
        rospy.loginfo("No se capturo imagen")

rospy.sleep(1)
