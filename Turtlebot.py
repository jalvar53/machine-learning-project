import rospy
from geometry_msgs.msg import Twist
from sklearn.externals import joblib

class Turtlebot:

    def __init__(self):
        self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        rospy.on_shutdown(self.shutdown)
        self.model = None

    def retrieve(self):
        self.model = joblib.load('model.pk1')

    def predict(self):
        a = None

    def move(self):
        msg = Twist()
        msg.linear.x = 0.2
        msg.angular.z = 0
        rate.sleep()
        self.publisher.publish(msg)

    def shutdown(self):
        rospy.loginfo("Stopping Turtlebot")
        self.publisher.publish(Twist())
        rospy.sleep(1)

if __name__ == '__main__':
    rospy.init_node('Turtlebot', anonymous=False)
    turtlebot = Turtlebot()
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        turtlebot.move()

