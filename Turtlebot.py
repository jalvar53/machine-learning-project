import rospy
from geometry_msgs.msg import Twist
from SvmModel import SvmModel
import ImageManager
import numpy as np
import cv2
import time


class Turtlebot:

    def __init__(self):
        #self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        #rospy.on_shutdown(self.shutdown)
        self.svm = SvmModel()
        self.x = 0

    def move(self,p,s):
        msg = Twist()
        print(p[84-s:96-s])
        print(p[96-s:108-s])
        left = sum(p[84-s:88-s])
        central = sum(p[88-s:92-s])
        rigth = sum(p[92-s:96-s])
        lefts = sum(p[96-s:100-s])
        rigths = sum(p[104-s:108-s])
        if(central > 2):
            #msg.linear.x = 0.2
            #msg.angular.z = 0
            print("moverse alante")
        elif(left > 2 or lefts > 2):
            # msg.linear.x = 0
            # msg.angular.z = 0.2
            print("mover a la izquierda")
        elif(rigth > 2 or rigths > 2):
            # msg.linear.x = 0
            # msg.angular.z = -0.2
            print("mover a la derecha")
        elif(left > 1 or lefts > 1):
            # msg.linear.x = 0
            # msg.angular.z = 0.4
            print("mover a la izquierda")
        elif(rigth > 1 or rigths > 1):
            # msg.linear.x = 0
            # msg.angular.z = -0.4
            print("mover a la derecha")
        elif(left > 0 or lefts > 0):
            # msg.linear.x = 0
            # msg.angular.z = 0.8
            print("mover a la izquierda")
        elif(rigth > 0 or rigths > 0):
            # msg.linear.x = 0
            # msg.angular.z = -0.8
            print("mover a la derecha")
        else:
            # msg.linear.x = 0.2
            # msg.angular.z = 0
            print("metale reversa")
        # rate.sleep()
        # self.publisher.publish(msg)

    def shutdown(self):
        rospy.loginfo("Stopping Turtlebot")
        self.publisher.publish(Twist())
        rospy.sleep(1)


if __name__ == '__main__':
    #rospy.init_node('Turtlebot', anonymous=False)
    turtlebot = Turtlebot()
    turtlebot.svm.load_model()
    #rate = rospy.Rate(10)

    for i in range(50):
        #t = time.time()
        img_name = 'assets/raw/frame' + str(int(i/1000))
        num = i%1000
        img_name += str(int(num/100))
        num = num % 100
        img_name += str(int(num/10)) + str(int(num%10))
        image = ImageManager.load_image(img_name)
        parts = ImageManager.slice_image(image,9,12)
        p=[]
        for j in range(84,108):
            x = ImageManager.retrieve_data(parts[j])
            p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1,13))))
        #print(p)
        turtlebot.move(p,84)
        cv2.imshow(img_name , image)
        cv2.waitKey()
        cv2.destroyAllWindows()
        #print("tiempo para ejemplo %d: %f" % (i,time.time()-t))


    # segments = ImageManager.slic_image(image,100)
    # turtlebot.svm.load_model()
    # mask = turtlebot.svm.predict(image, segments)
    # print(mask)
    #
    # while not rospy.is_shutdown():
    #     turtlebot.move()
