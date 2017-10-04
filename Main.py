import rospy
import numpy as np
from geometry_msgs.msg import Twist
from sklearn import svm
import Math as math
import Trainer
import Turtlebot
import ImageProcessor
import cv2
import time

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
    while(np.sum(y) == 0):
        turtlebot.move_around(pub)
        turtlebot.retrieve_data()
        x, y = trainer.get_x_y()
    model_trainer = svm.SVC()
    model_trainer.fit(x, y.reshape((x.shape[0])))

    for i in range(100):
        #t = time.time()
        turtlebot.refresh_image()
        #print("tiempo refrescar imagen: %f" %(time.time()-t))
        #t = time.time()
        turtlebot.retrieve_data()
        #print("tiempo sacar datos: %f" %(time.time()-t))
        #t = time.time()
        x, y = trainer.get_x_y()
        i = 0
        while(np.sum(y) == 0 and i < 100):
            turtlebot.move_around(pub)
            turtlebot.retrieve_data()
            x, y = trainer.get_x_y()
        # i = 0

        # while (i < 1000):
        #cv2.imshow("miNombre", turtlebot.image)
        #cv2.waitKey(33)
        #     i += 1
        #     # print(i)
        p = model_trainer.predict(x)
        turtlebot.move(pub,p)
    #print(model_trainer.predict([[155, 155, 155, 0], [153.5, 153.5, 153.5, 0], [156.85, 156.85, 156.85, 0], [156.5, 156.5, 156.5, 0]]))

rospy.sleep(1)
