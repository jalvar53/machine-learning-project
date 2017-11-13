import numpy as np
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

fase = 0

def response(msg, cont):
    global fase
    pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    #rate = rospy.Rate(10)
    #if((msg.pose.pose.position.x < -0.3 or msg.pose.pose.position.x > 0.7) or (msg.pose.pose.position.y < -0.7 or msg.pose.pose.position.y > 0.3)):

    if(fase == 0):
        if(msg.pose.pose.position.x < 2.5):
            msg2 = Twist()
            msg2.linear.x=0.3
            msg2.angular.z=0.02
            pub.publish(msg2)
            print(msg.pose.pose.position.x)
        else:
            fase = 1
    elif(fase == 1):
        if(abs(msg.pose.pose.orientation.z) < 0.4):
            msg2 = Twist()
            msg2.angular.z=-1
            pub.publish(msg2)
            print(abs(msg.pose.pose.orientation.z))
        else:
            msg2 = Twist()
            msg2.angular.z=0
            pub.publish(msg2)
            fase = 2
    elif(fase == 2):
        if(msg.pose.pose.position.y > -1.9):
            msg2 = Twist()
            msg2.linear.x=0.3
            msg2.angular.z=0.02
            pub.publish(msg2)
            print(msg.pose.pose.position.y)
        else:
            fase = 3
    elif(fase == 3):
        if(abs(msg.pose.pose.orientation.z) < 0.95):
            msg2 = Twist()
            msg2.angular.z=-1
            pub.publish(msg2)
            print(abs(msg.pose.pose.orientation.z))
        else:
            msg2 = Twist()
            msg2.angular.z=0
            pub.publish(msg2)
            fase = 4
    elif(fase == 4):
        if(msg.pose.pose.position.x > 0):
            msg2 = Twist()
            msg2.linear.x=0.3
            msg2.angular.z=0.02
            pub.publish(msg2)
            print(msg.pose.pose.position.x)
        else:
            fase = 5
    elif(fase == 5):
        if(abs(msg.pose.pose.orientation.z) > 0.87):
            msg2 = Twist()
            msg2.angular.z=-1
            pub.publish(msg2)
            print(abs(msg.pose.pose.orientation.z))
        else:
            msg2 = Twist()
            msg2.angular.z=0
            pub.publish(msg2)
            fase = 6
    elif(fase == 6):
        if(msg.pose.pose.position.y < 0):
            msg2 = Twist()
            msg2.linear.x=0.3
            msg2.angular.z=0.02
            pub.publish(msg2)
            print(msg.pose.pose.position.y)
        else:
            fase = 7

    #rospy.sleep(0.01)
    # if(msg.pose.pose.position.x < 2.8 and fase < 1):
    #     fase = 0
    #     msg2 = Twist()
    #     msg2.linear.x=0.3
    #     msg2.angular.z=0.02
    #     pub.publish(msg2)
    #     #print(msg.pose.pose.position.x, msg.pose.pose.position.y)
    # elif(msg.pose.pose.orientation.w < -0.7 or msg.pose.pose.orientation.w > -0.6 or msg.pose.pose.orientation.z < 0.8 or msg.pose.pose.orientation.z > 0.7 and fase < 2):
    #     fase = 1
    #     msg2 = Twist()
    #     msg2.angular.z=1
    #     pub.publish(msg2)
    #     #print(msg.pose.pose.orientation)

rospy.init_node('moveOdom', anonymous=False)
cont = 0
#while not rospy.is_shutdown():
    #print(fase)
sub = rospy.Subscriber('odom', Odometry, response, callback_args=cont)
rospy.spin()

# if __name__ == '__main__':
#     rospy.init_node('moveOdom', anonymous=False)
#     band = False
#     cont = 0
#     while not rospy.is_shutdown():
#         if(not band):
#             cont = 0
#         else:
#             cont = 1
#         sub = rospy.Subscriber('odom', Odometry, response, callback_args=cont)
        #print(sub)
    #response(sub)
    #print(response(sub))
    #rospy.spin()

    #point: x: 0.2, y: -0.2
