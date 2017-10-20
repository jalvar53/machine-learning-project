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

    def categories(self):
        self.cats = [0,0,0,0,0,0,0,0,0,0,
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
        return self.cats

    def move(self, p, s):
        msg = Twist()
        print(p[84-s:96-s])
        print(p[96-s:108-s])
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


if __name__ == '__main__':
    turtlebot = Turtlebot()
    turtlebot.svm.load_model()
    performance = 0
    for i in range(100,150):
        img_name = 'assets/raw/frame' + str(int(i/1000))
        num = i%1000
        img_name += str(int(num/100))
        num = num % 100
        img_name += str(int(num/10)) + str(int(num%10))
        image = ImageManager.load_image(img_name)
        parts = ImageManager.slice_image(image, 9, 12)
        type(image)
        p = []
        for j in range(84, 108):
            x = ImageManager.retrieve_data(parts[j])
            p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1, len(x)))))
        turtlebot.move(p, 84)
        if turtlebot.pred[i-100]==turtlebot.categories()[i]:
            performance += 1
        cv2.imshow(img_name, image)
        cv2.waitKey()
        cv2.destroyAllWindows()
    print(performance)
