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
        self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        rospy.sleep(1)
        rospy.on_shutdown(self.shutdown)
        self.svm = SvmModel()
        self.x = 0
        self.stage = 0
        self.aim="ahead"
        self.p_prev = [0]
        self.pred = []
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

    def girar(self, dire):
        #si dire es uno gira a izq si es -1 gira a derecha
        send = Twist()
        r = rospy.Rate(5);
        for x in range(0,10):
            send.linear.x = 0
            send.angular.z = radians(45*dire)
            r.sleep()
            print("girando")
            self.publisher.publish(send)

    def move(self, msg):
        #image = self.image
        #cv2.namedWindow("whate");
        #cv2.moveWindow("whate", 710,280);
        #cv2.imshow("whate", turtlebot.image)
        imageBaW = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        parts2, parts2_hsv, parts2_BaW, segments = ImageManager.slic_image(self.image, imageBaW, 9, 12)
        p2 = []
        for j in range(108):
            x2 = ImageManager.retrieve_data2(parts2[j], parts2_hsv[j], parts2_BaW[j])
            p2.append(int(turtlebot.svm.get_model().predict(np.asarray(x2).reshape(1, len(x2)))))

        send = Twist()
        #r = rospy.Rate(5);
        p = p2
        s=0
        #if(len(p)>1):
        #print(p[84-s:96-s])
        #print(p[96-s:108-s])
        left = sum(p[84-s:88-s])
        central = sum(p[88-s:92-s])
        right = sum(p[92-s:96-s])
        lefts = sum(p[96-s:100-s])
        rights = sum(p[104-s:108-s])
        #self.stage = 200
        #print(central)
        if(not(self.p_prev == p)):
            self.p_prev = p
            #print("entra")
            if(self.stage == 0):
                ##guardar posicion inicial
                self.ini_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
                self.stage=1
            elif(self.stage==1):
                ##moverse hasta 13.5 de distancia
                print(self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos))
                if(self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos) < 1):
                    #print("central: %d" % central)
                    if(central > 2):
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                    else:
                        print("esquivar")
                        if(left + lefts > right + rights):
                            self.girar(1)
                            self.aim="left"
                        else:
                            self.girar(-1)
                            self.aim="right"
                        self.prev_stage = 1
                        self.stage=100
                else:
                    r = rospy.Rate(5);
                    for x in range(0,10):
                        send.linear.x = 0
                        send.angular.z = radians(75)
                        r.sleep()
                        print("girando")
                        self.publisher.publish(send)
                    self.stage = 200
            elif(self.stage == 2):
                ##guardar posicion inicial
                self.ini_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
                self.stage=3
            elif(self.stage == 3):
                ##moverse hasta 26 de distancia
                if(self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos) < 26):
                    if(central > 2):
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                    else:
                        self.esquivar() ################no es funcion
                        if(left + lefts > rigth + rigths):
                            self.girar(1)
                            self.aim="left"
                        else:
                            self.girar(-1)
                            self.aim="right"
                        self.prev_stage = 1
                        self.stage=100
                else:
                    r = rospy.Rate(5);
                    for x in range(0,10):
                        send.linear.x = 0
                        send.angular.z = radians(45)
                        r.sleep()
                        print("girando")
                        self.publisher.publish(send)
                    self.stage = 4
            elif(self.stage==4):
                ##guardar posicion inicial
                self.ini_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
                self.stage=5
            elif(self.stage==5):
                ##moverse hasta 13.5 de distancia
                if(self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos) < 13.5):
                    if(central > 2):
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                    else:
                        self.esquivar() ################no es funcion
                        if(left + lefts > rigth + rigths):
                            self.girar(1)
                            self.aim="left"
                        else:
                            self.girar(-1)
                            self.aim="right"
                        self.prev_stage = 1
                        self.stage=100
                else:
                    r = rospy.Rate(5);
                    for x in range(0,10):
                        send.linear.x = 0
                        send.angular.z = radians(45)
                        r.sleep()
                        print("girando")
                        self.publisher.publish(send)
                    self.stage = 6
            elif(self.stage==6):
                ##guardar posicion inicial
                self.ini_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
                self.stage=7
            elif(self.stage==7):
                ##moverse hasta 26 de distancia
                if(self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos) < 26):
                    if(central > 2):
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                    else:
                        #self.esquivar() ################no es funcion
                        if(left + lefts > rigth + rigths):
                            self.girar(1)
                            self.aim="left"
                        else:
                            self.girar(-1)
                            self.aim="right"
                        self.prev_stage = 1
                        self.stage=100
                    print("Move forward")
                else:
                    r = rospy.Rate(5);
                    for x in range(0,10):
                        send.linear.x = 0
                        send.angular.z = radians(45)
                        r.sleep()
                        print("girando")
                        self.publisher.publish(send)
                    self.stage = 8
            elif(self.stage==8):
                print("hemos dado una vuelta")
            elif(self.stage == 100):
                ##esquivar A
                print("esquivar AAAAAAAAAAAAAAAAAAAAAA")
                if(self.aim=="left"):
                    if(right + rights > 4):
                        #print "pasa a BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
                        self.girar(-1)
                        self.stage = 101
                    else:
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                else:
                    if(left + lefts > 4):
                        #print "pasa a BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB XD"
                        self.girar(1)
                        self.stage = 101
                    else:
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
            elif(self.stage == 101):
                ##esquivar B
                print("esquivar BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                if(self.aim=="left"):
                    print("Right: %d" % right)
                    print("Rights: %d   " % rights)
                    if(right + rights > 4):
                        self.girar(-1)
                        self.stage = 102
                        self.aim= "right"
                    else:
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
                else:
                    if(left + lefts > 4):
                        self.girar(1)
                        self.stage = 102
                        self.aim="left"
                    else:
                        send.linear.x = 0.2
                        send.angular.z = 0
                        print("Move forward")
            elif(self.stage==102):
                #esquivar c
                print("esquivar CCCCCCCCCCCCCCCCCCCCCCCC")
                if(self.aim == "left"):
                    if(self.prev_stage == 1):
                        if(msg.pose.pose.position.y < self.ini_pos[1]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 3):
                        if(msg.pose.pose.position.x < self.ini_pos[0]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 5):
                        if(msg.pose.pose.position.y > self.ini_pos[1]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 7):
                        if(msg.pose.pose.position.x > self.ini_pos[0]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                else:
                    if(self.prev_stage == 1):
                        if(msg.pose.pose.position.y < self.ini_pos[1]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 3):
                        if(msg.pose.pose.position.x > self.ini_pos[0]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 5):
                        if(msg.pose.pose.position.y < self.ini_pos[1]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage
                    elif(self.prev_stage == 7):
                        if(msg.pose.pose.position.x < self.ini_pos[0]):
                            send.linear.x = 0.2
                            send.angular.z = 0
                            print("Move forward")
                        else:
                            self.girar(-1)
                            self.stage = self.prev_stage

            self.publisher.publish(send)



        #print(self.ini_pos, "aca")
        #print(msg.pose.pose.position.x,msg.pose.pose.position.y)
        #print self.get_distance((msg.pose.pose.position.x, msg.pose.pose.position.y), self.ini_pos)
        self.publisher.publish(send)

        # destination = [-6,0]
        # print(msg.pose.pose.position.x,msg.pose.pose.position.y)
        # if(msg.pose.pose.position.x > destination[0]):
        #     send.linear.x = 0.2
        #     send.angular.z = 0
        #     self.pred.append(0)
        #     print("Move forward")
        # elif (self.stage==0):
        #     for x in range(0,10):
        #         send.linear.x = 0
        #         send.angular.z = radians(45)
        #         r.sleep()
        #     self.stage = 1
        # self.publisher.publish(send)

        # if central > 2:
        #     msg.linear.x = 0.2
        #     msg.angular.z = 0
        #     self.pred.append(0)
        #     print("Move forwards")
        # elif left > 2 or lefts > 2:
        #     msg.linear.x = 0
        #     msg.angular.z = 0.5
        #     self.pred.append(3)
        #     print("Move left")
        # elif right > 2 or rights > 2:
        #     msg.linear.x = 0
        #     msg.angular.z = -0.5
        #     self.pred.append(1)
        #     print("Move right")
        # elif left > 1 or lefts > 1:
        #     msg.linear.x = 0
        #     msg.angular.z = 0.8
        #     self.pred.append(3)
        #     print("Move left")
        # elif right > 1 or rights > 1:
        #     msg.linear.x = 0
        #     msg.angular.z = -0.8
        #     self.pred.append(1)
        #     print("Move right")
        # elif left > 0 or lefts > 0:
        #     msg.linear.x = 0
        #     msg.angular.z = 1.2
        #     self.pred.append(3)
        #     print("Move left")
        # elif right > 0 or rights > 0:
        #     msg.linear.x = -0.2
        #     msg.angular.z = 0
        #     self.pred.append(1)
        #     print("Move backwards")
        # else:
        #     msg.linear.x = -0.2
        #     msg.angular.z = 0
        #     self.pred.append(2)
        #     print("Move backwards")
        # rate.sleep()
        # self.publisher.publish(msg)

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
    rate = rospy.Rate(10)
    while not turtlebot.image_received:
        pass
    while not rospy.is_shutdown():
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
        rospy.Subscriber('odom', Odometry, turtlebot.move)
        #turtlebot.debug2(p2, turtlebot.image, segments)
        #cv2.waitKey()
        #cv2.destroyAllWindows()
