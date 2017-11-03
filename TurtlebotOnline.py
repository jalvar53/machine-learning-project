import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from SvmModel import SvmModel
from cv_bridge import CvBridge, CvBridgeError
import ImageManager
import numpy as np
import cv2


class Turtlebot:

    def __init__(self):
        self.bridge = CvBridge()
        self.image_received = False
        self.image = None
        self.img_subscriber = rospy.Subscriber('/camera/rgb/image_raw', Image, self.callback)
        self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        rospy.sleep(1)
        rospy.on_shutdown(self.shutdown)
        self.svm = SvmModel()
        self.x = 0
        self.pred = []
        self.exp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1, 2, 3, 3,
                     0, 0, 0, 0, 0, 0, 0, 3, 0, 0,
                     0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
                     3, 0, 0, 3, 3, 0, 0, 3, 3, 0,
                     0, 0, 1, 1, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                     0, 1, 1, 2, 3, 3, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                     1, 1, 0, 0, 0, 0, 0, 0, 3, 3,
                     3, 0, 1, 1, 1, 0, 0, 0, 0, 0,
                     3, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0]

    def get_desired_values(self):
        return self.exp

    def move(self, p, s):
        msg = Twist()
        print(p[84-s:96-s])
        print(p[96-s:108-s])
        left = sum(p[84-s:88-s])
        central = sum(p[88-s:92-s])
        right = sum(p[92-s:96-s])
        lefts = sum(p[96-s:100-s])
        rights = sum(p[104-s:108-s])
        if central > 2:
            msg.linear.x = 0.2
            msg.angular.z = 0
            self.pred.append(0)
            print("Move forwards")
        elif left > 2 or lefts > 2:
            msg.linear.x = 0
            msg.angular.z = 0.2
            self.pred.append(3)
            print("Move left")
        elif right > 2 or rights > 2:
            msg.linear.x = 0
            msg.angular.z = -0.2
            self.pred.append(1)
            print("Move right")
        elif left > 1 or lefts > 1:
            msg.linear.x = 0
            msg.angular.z = 0.4
            self.pred.append(3)
            print("Move left")
        elif right > 1 or rights > 1:
            msg.linear.x = 0
            msg.angular.z = -0.4
            self.pred.append(1)
            print("Move right")
        elif left > 0 or lefts > 0:
            msg.linear.x = 0
            msg.angular.z = 0.8
            self.pred.append(3)
            print("Move left")
        elif right > 0 or rights > 0:
            msg.linear.x = -0.2
            msg.angular.z = 0
            self.pred.append(1)
            print("Move backwards")
        else:
            msg.linear.x = -0.2
            msg.angular.z = 0
            self.pred.append(2)
            print("Move backwards")
        rate.sleep()
        self.publisher.publish(msg)

    def shutdown(self):
        rospy.loginfo("Stopping Turtlebot")
        self.publisher.publish(Twist())
        rospy.sleep(1)

    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
        self.image_received = True
        self.image = cv_image

def debug(self, p, image):
    self.imageBaW = image[:,:,:]
    height, width, channels = self.imageBaW.shape
    height = height / 9
    width = width / 12
    for i in range(len(p)):
        if(p[i]):
            self.imageBaW[int(i/12) * height:(int(i/12) + 1) * height, int(i%12) * width:(int(i%12) + 1) * width]=255
        else:
            self.imageBaW[int(i/12) * height:(int(i/12) + 1) * height, int(i%12) * width:(int(i%12) + 1) * width]=0
    cv2.imshow("debug", self.imageBaW)

def debug2(self, p, image, segments):
    self.imageBaW = np.zeros((image.shape))
    for (i, segVal) in enumerate(np.unique(segments)):
        if(p[i]):
            self.imageBaW[segments==segVal]=255
        else:
            self.imageBaW[segments==segVal]=0
    cv2.imshow("debug2", self.imageBaW)

if __name__ == '__main__':
    turtlebot = Turtlebot()
    rospy.init_node('Turtlebot', anonymous=False)
    turtlebot.svm.load_model()
    rate = rospy.Rate(10)
    while not turtlebot.image_received:
        pass
    while not rospy.is_shutdown():
        ##implementacion diviendo imagen en cuadros
        # image = turtlebot.image
        # cv2.imshow("whate", turtlebot.image)
        # #cv2.waitKey(5000)
        # #cv2.destroyAllWindows()
        # parts = ImageManager.slice_image(turtlebot.image, 9, 12)
        # p = []
        # for j in range(84, 108):
        #     x = ImageManager.retrieve_data(parts[j])
        #     p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1, 13))))
        # # print(p)
        # turtlebot.move(p, 84)
        # turtlebot.debug(p, turtlebot.image)
        # cv2.waitKey(5000)
        # cv2.destroyAllWindows()

        ##implementacion de superpixeles
        image = turtlebot.image
        cv2.imshow("whate", turtlebot.image)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()
        parts2,segments = ImageManager.slic_image(turtlebot.image, 9, 12)
        p2 = []
        for j in range(84, 108):
            x2 = ImageManager.retrieve_data2(parts2[j])
            p2.append(int(turtlebot.svm.get_model().predict(np.asarray(x2).reshape(1, 13))))
        # print(p)
        turtlebot.move(p2, 84)
        turtlebot.debug2(p2, turtlebot.image, segments)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()
