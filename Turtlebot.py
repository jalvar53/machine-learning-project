import rospy
from geometry_msgs.msg import Twist
from SvmModel import SvmModel
import ImageManager


class Turtlebot:

    def __init__(self):
        self.publisher = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        rospy.on_shutdown(self.shutdown)
        self.svm = SvmModel()
        self.x = 0

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

    image = ImageManager.load_image("assets/raw/frame0040")
    segments = ImageManager.slic_image(image,100)
    turtlebot.svm.load_model()
    mask = turtlebot.svm.predict(image, segments)
    print(mask)

    while not rospy.is_shutdown():
        turtlebot.move()

