import rospy
from geometry_msgs.msg import Twist

rospy.init_node('classifier', anonymous=False)
pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
r = rospy.Rate(10)

msg = Twist()
msg.linear.x = 0.2
msg.angular.z = 0

for i in range(100):

    pub.publish(msg)
    r.sleep()

rospy.sleep(1)