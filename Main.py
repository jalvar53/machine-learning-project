import rospy
import numpy as np
from geometry_msgs.msg import Twist
import Math as math
import Trainer
import Turtlebot
import ImageProcessor

if __name__ == '__main__':
    trainer = Trainer.Trainer()
    turtlebot = Turtlebot.Turtlebot(trainer)
    imgProcessor = ImageProcessor.ImageProcessor(turtlebot)
    rospy.init_node('classifier', anonymous=False)
    pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    imgProcessor.find_floor_values()
    title = rospy.get_param('~image_title', 'image.jpg')
    if imgProcessor.save_image(title):
        rospy.loginfo("Image saved " + title)
    else:
        rospy.loginfo("No image captured")
    turtlebot.retrieve_data()
    x, y = trainer.get_x_y()
    theta = trainer.gradient_descent(100, 0.01, 100)
    h = math.sigmoid(np.einsum('ij,jk', x, theta))
    maxi = 0
    mini = 100001
    for i in range(y.shape[0]):
        if not (y[i]) and h[i] < mini:
            mini = h[i]
        elif y[i] and h[i] > maxi:
            maxi = h[i]
    sol = np.zeros((x.shape[0], x.shape[1]+1), 'float')
    sol[:, 0] = x[:, 0]
    sol[:, 1] = x[:, 1]
    sol[:, 2] = x[:, 2]
    sol[:, 3] = x[:, 3]
    sol[:, 4] = y.reshape(108)
    print(sol)
    print(h)
    print("Maximum: %f Minimun: %f" % (maxi, mini))
    print(math.probability([1, 1, 1, 3.13423863e-300], theta))

rospy.sleep(1)
