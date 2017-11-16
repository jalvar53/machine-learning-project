import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from SvmModel import SvmModel
from cv_bridge import CvBridge, CvBridgeError
from math import radians, sqrt
import ImageManager
import numpy as np
import cv2

class Turtlebot:

    def __init__(self):
        self.bridge = CvBridge()
        self.image_received = False
        self.image = None
        self.img_subscriber = rospy.Subscriber('/camera/rgb/image_raw', Image, self.callback)
        self.pos_subscriver = rospy.Subscriber('odom', Odometry, self.pos_update)
        self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        rospy.sleep(1)
        rospy.on_shutdown(self.shutdown)
        self.svm = SvmModel()
        self.x = 0
        self.stage = 0
        self.aim="ahead"
        self.p_prev = [0]
        self.pred = []
        self.cont = 0
        self.ini_pos = [0,0]
        self.prev_stage = 0
        self.ini_pose = [0,0]
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

    def get_distance(self,a,b):
        return (sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2))

    def andar(self):
        send = Twist()
        send.linear.x = 0.2
        send.angular.z = 0
        self.publisher.publish(send)
        print("Move forward")

    def girar(self, dire):
        #si dire es uno gira a izq si es -1 gira a derecha
        send = Twist()
        r = rospy.Rate(5);
        send.linear.x = 0
        send.angular.z = 0
        print("parando")
        self.publisher.publish(send)
        r.sleep()
        for x in range(0,10):
            send.linear.x = 0
            send.angular.z = radians(45*dire)
            print("girando")
            self.publisher.publish(send)
            r.sleep()

    def move(self):
        position = self.position
        orientation = self.orientation
        image = self.image
        cv2.namedWindow("original");
        cv2.moveWindow("original", 710,280);
        cv2.imshow("original", image)
        imageBaW = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        parts, parts_hsv, parts_BaW, segments = ImageManager.slic_image(image, imageBaW, 9, 12)
        p = []
        for j in range(108):
            x = ImageManager.retrieve_data2(parts[j], parts_hsv[j], parts_BaW[j])
            p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1, len(x)))))
        self.debug2(p, self.image, segments)
        cv2.waitKey(500)
        #cv2.destroyAllWindows()
        #send = Twist()
        #print(p[72-s:84-s])
        #print(p[84-s:96-s])
        #print(p[96-s:108-s])
        left = sum(p[72:76])
        central = sum(p[88:92])
        right = sum(p[80:84])
        lefts = sum(p[84:88])
        rights = sum(p[92:96])
        if(self.stage > 0):
            print("distancia: %f" % self.get_distance((position.x, position.y), self.ini_pos))
        if(self.stage == 0):
            ##guardar posicion inicial
            self.ini_pos = (position.x, position.y)
            self.stage=1
        elif(self.stage == 1):
            ##moverse hasta 26 de distancia
            if(self.get_distance((position.x, position.y), self.ini_pos) < 26):
                if(central > 2):
                    self.andar()
                else:
                    if(left + lefts > right + rights):
                        self.girar(1)
                        self.aim="left"
                    else:
                        self.girar(-1)
                        self.aim="right"
                    self.prev_stage = 1
                    self.stage=100
            else:
                self.girar(1)
                self.stage = 2
        elif(self.stage==2):
            ##guardar posicion inicial
            self.ini_pos = (position.x, position.y)
            self.stage=3
        elif(self.stage==3):
            ##moverse hasta 13.5 de distancia
            if(self.get_distance((position.x, position.y), self.ini_pos) < 13.5):
                if(central > 2):
                    self.andar()
                else:
                    if(left + lefts > right + rights):
                        self.girar(1)
                        self.aim="left"
                    else:
                        self.girar(-1)
                        self.aim="right"
                    self.prev_stage = 3
                    self.stage=100
            else:
                self.girar(1)
                self.stage = 4
        elif(self.stage==4):
            ##guardar posicion inicial
            self.ini_pos = (position.x, position.y)
            self.stage=5
        elif(self.stage==5):
            ##moverse hasta 26 de distancia
            if(self.get_distance((position.x, position.y), self.ini_pos) < 26):
                if(central > 2):
                    self.andar()
                else:
                    if(left + lefts > right + rights):
                        self.girar(1)
                        self.aim="left"
                    else:
                        self.girar(-1)
                        self.aim="right"
                    self.prev_stage = 5
                    self.stage=100
                print("Move forward")
            else:
                self.girar(1)
                self.stage = 6
        elif(self.stage == 6):
            ##guardar posicion inicial
            self.ini_pos = (position.x, position.y)
            self.stage=7
        elif(self.stage==7):
            ##moverse hasta 13.5 de distancia
            if(self.get_distance((position.x, position.y), self.ini_pos) < 13.5):
                if(central > 2):
                    self.andar()
                else:
                    print("esquivar")
                    if(left + lefts > right + rights):
                        self.girar(1)
                        self.aim="left"
                    else:
                        self.girar(-1)
                        self.aim="right"
                    self.prev_stage = 7
                    self.stage=100
            else:
                self.girar(1)
                self.stage = 8
        elif(self.stage==8):
            print("hemos dado una vuelta")
        elif(self.stage == 100):
            ##esquivar A
            print("esquivar AAAAAAAAAAAAAAAAAAAAAA")
            self.andar()
            self.cont += 1
            if(self.aim=="left"):
                self.girar(-1)
                self.stage = 101
            else:
                self.girar(1)
                self.stage = 101
        elif(self.stage == 101):
            if(central > 2):
                self.stage = 102
            else:
                if(self.aim=="left"):
                    self.girar(1)
                    self.stage = 100
                else:
                    self.girar(-1)
                    self.stage = 100
        elif(self.stage == 102):
            ##esquivar B
            print("esquivar BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
            self.andar()
            print("move forward")
            if(self.aim=="left"):
                self.girar(-1)
                self.stage = 103
            else:
                self.girar(1)
                self.stage = 103
        elif(self.stage==103):
            if(central > 2):
                self.stage = 104
                if(self.aim=="left"):
                    self.aim = "right"
                else:
                    self.aim = "left"
            else:
                if(self.aim=="left"):
                    self.girar(1)
                    self.stage = 102
                else:
                    self.girar(-1)
                    self.stage = 102
        elif(self.stage==104):
            #esquivar c
            print("esquivar CCCCCCCCCCCCCCCCCCCCCCCC")
            if(self.aim == "left"):
                if(self.cont > 0):
                    self.andar()
                    self.cont -= 1
                else:
                    self.girar(-1)
                    self.stage = self.prev_stage
            else:
                if(self.cont > 0):
                    self.andar()
                    self.cont -= 1
                else:
                    self.girar(1)
                    self.stage = self.prev_stage

    def shutdown(self):
        rospy.loginfo("Stopping Turtlebot")
        self.publisher.publish(Twist())
        rospy.sleep(1)
        cv2.destroyAllWindows()

    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
        self.image_received = True
        self.image = cv_image

    def pos_update(self, msg):
        self.position = msg.pose.pose.position
        self.orientation = msg.pose.pose.orientation

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

    def move_try(self, msg):
        print(msg.pose.pose.position)

if __name__ == '__main__':
    turtlebot = Turtlebot()
    rospy.init_node('Turtlebot', anonymous=False)
    turtlebot.svm.load_model()
    while not turtlebot.image_received:
        pass
    while not rospy.is_shutdown():
        turtlebot.move()







        ##implementacion diviendo imagen en cuadros
        # image = turtlebot.image
        # cv2.namedWindow("whate");
        # cv2.moveWindow("whate", 710,280);
        # cv2.imshow("whate", turtlebot.image)
        # imageBaW = cv2.cvtColor(turtlebot.image, cv2.COLOR_BGR2GRAY)
        # parts, parts_hsv, parts_BaW = ImageManager.slice_image(turtlebot.image,  imageBaW, 9, 12)
        # p = []
        # for j in range(84, 108):
        #     x = ImageManager.retrieve_data(parts[j], parts_hsv[j], parts_BaW[j])
        #     p.append(int(turtlebot.svm.get_model().predict(np.asarray(x).reshape(1, len(x)))))
        # turtlebot.move(p, 84)
        # turtlebot.debug(p, turtlebot.image)
        # cv2.waitKey(5000)
        # cv2.destroyAllWindows()

        ##*************+implementacion de superpixeles**************************
        # image = turtlebot.image
        # #cv2.namedWindow("whate");
        # #cv2.moveWindow("whate", 710,280);
        # #cv2.imshow("whate", turtlebot.image)
        # imageBaW = cv2.cvtColor(turtlebot.image, cv2.COLOR_BGR2GRAY)
        # parts2, parts2_hsv, parts2_BaW, segments = ImageManager.slic_image(turtlebot.image, imageBaW, 9, 12)
        # p2 = []
        # for j in range(108):
        #     x2 = ImageManager.retrieve_data2(parts2[j], parts2_hsv[j], parts2_BaW[j])
        #     p2.append(int(turtlebot.svm.get_model().predict(np.asarray(x2).reshape(1, len(x2)))))
        #turtlebot.move(p2, 0)
        #rospy.Subscriber('odom', Odometry, turtlebot.move)
        #turtlebot.debug2(p2, turtlebot.image, segments)
        #cv2.waitKey()
        #cv2.destroyAllWindows()
