import rospy
from geometry_msgs.msg import Twist
from SvmModel import SvmModel
import ImageManager
import numpy as np
import cv2
import time


class Turtlebot:

    def __init__(self):
        self.svm = SvmModel()
        self.x = 0
        self.pred=[]
        self.exp = [0,0,0,0,0,0,0,0,0,0,
                     0,0,0,0,0,0,1,2,3,3,
                     0,0,0,0,0,0,0,3,0,0,
                     0,0,3,0,0,0,0,0,0,0,
                     0,0,3,0,0,0,0,0,0,0,
                     3,0,0,3,3,0,0,3,3,0,
                     0,0,1,1,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,0,0,0,
                     0,0,0,0,0,1,0,0,0,0,
                     0,1,1,2,3,3,0,0,0,0,
                     0,0,0,0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,0,0,0,
                     0,0,0,0,0,0,1,1,1,1,
                     1,1,0,0,0,0,0,0,3,3,
                     3,0,1,1,1,0,0,0,0,0,
                     3,3,1,1,0,0,0,0,0,0,0]

    def get_desired_values(self):
        return self.exp

    def move(self, p, s):
        msg = Twist()
        #print(p[84-s:96-s])
        #print(p[96-s:108-s])
        left = sum(p[84-s:88-s])
        central = sum(p[88-s:92-s])
        rigth = sum(p[92-s:96-s])
        lefts = sum(p[96-s:100-s])
        rigths = sum(p[104-s:108-s])
        if central > 2:
            self.pred.append(0)
            print("moverse alante")
        elif left > 2 or lefts > 2:
            self.pred.append(3)
            print("mover a la izquierda")
        elif rigth > 2 or rigths > 2:
            self.pred.append(1)
            print("mover a la derecha")
        elif left > 1 or lefts > 1:
            self.pred.append(3)
            print("mover a la izquierda")
        elif rigth > 1 or rigths > 1:
            self.pred.append(1)
            print("mover a la derecha")
        elif left > 0 or lefts > 0:
            self.pred.append(3)
            print("mover a la izquierda")
        elif rigth > 0 or rigths > 0:
            self.pred.append(1)
            print("mover a la derecha")
        else:
            self.pred.append(2)
            print("metale reversa")

    def shutdown(self):
        rospy.loginfo("Stopping Turtlebot")
        self.publisher.publish(Twist())
        rospy.sleep(1)

    def debug(self, p, image):
        self.imageBaW = np.zeros((image.shape))
        height, width, channels = self.imageBaW.shape
        height = height / 9
        width = width / 12
        for i in range(len(p)):
            if(p[i]):
                self.imageBaW[int(i/12) * height:(int(i/12) + 1) * height, int(i%12) * width:(int(i%12) + 1) * width]=255
            else:
                self.imageBaW[int(i/12) * height:(int(i/12) + 1) * height, int(i%12) * width:(int(i%12) + 1) * width]=0
        cv2.namedWindow("debug");
        cv2.moveWindow("debug", 710,20);
        cv2.imshow("debug", self.imageBaW)

    def debug2(self, p, image, segments):
        self.imageBaW = np.zeros((image.shape))
        for (i, segVal) in enumerate(np.unique(segments)):
            if(p[i]):
                self.imageBaW[segments==segVal]=255
            else:
                self.imageBaW[segments==segVal]=0
        cv2.namedWindow("debug");
        cv2.moveWindow("debug", 710,20);
        cv2.imshow("debug", self.imageBaW)

if __name__ == '__main__':
    turtlebot = Turtlebot()
    turtlebot.svm.load_model()
    performance = 0
    band = False
    start = 0
    cont=0.0
    for i in range(151,161):
        #***********implementacion diviendo la imagen en cuadros*******************
        # if(not band):
        #     start = i
        #     band = True
        # img_name = 'assets/raw/frame' + str(int(i/1000))
        # num = i%1000
        # img_name += str(int(num/100))
        # num = num % 100
        # img_name += str(int(num/10)) + str(int(num%10))
        # image, imageBaW = ImageManager.load_image(img_name)
        # parts, parts_hsv, parts_BaW = ImageManager.slice_image(image, 9, 12)
        # p = []
        # for j in range(108):
        #     x = ImageManager.retrieve_data(parts[j], parts_hsv[j], parts_BaW[j])
        #     p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1, len(x)))))
        # turtlebot.move(p, 0)
        # if turtlebot.pred[i-start]==turtlebot.get_desired_values()[i]:
        #     performance += 1
        # cv2.namedWindow(img_name);
        # cv2.moveWindow(img_name, 20,20);
        # cv2.imshow(img_name, image)
        # turtlebot.debug(p, image)
        # cv2.waitKey()
        # cv2.destroyAllWindows()


        #******************implementacion con superpixeles**************************
        t=time.time()
        if(not band):
            start = i
            band = True
        img_name = 'assets/raw/frame' + str(int(i/1000))
        num = i%1000
        img_name += str(int(num/100))
        num = num % 100
        img_name += str(int(num/10)) + str(int(num%10))
        image, imageBaW = ImageManager.load_image(img_name)
        parts2, parts2_hsv, parts2_BaW, segments = ImageManager.slic_image(image, imageBaW, 9, 12)
        p2 = []
        for j in range(108):
            x2 = ImageManager.retrieve_data2(parts2[j], parts2_hsv[j], parts2_BaW[j])
            p2.append(int(turtlebot.svm.get_model().predict(np.asarray(x2).reshape(1, len(x2)))))
        print("tiempo para calcular x y predecir total: %f" % (time.time()-t))
        turtlebot.move(p2, 0)
        if turtlebot.pred[i-start]==turtlebot.get_desired_values()[i]:
            performance += 1
        cont = cont + 1.0
        #cv2.namedWindow(img_name);
        #cv2.moveWindow(img_name, 710,280);
        #cv2.imshow(img_name, image)
        print("tiempo: %f" % (time.time()-t))
        #turtlebot.debug2(p2, image, segments)
        #cv2.waitKey()
        #cv2.destroyAllWindows()
    print("performance: %.2f%%" %( performance/cont*100 ))
