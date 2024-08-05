import rospy
from std_srvs.srv import Trigger, TriggerResponse
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import Bool, Int32, Int16, Float64

class timestamp_ctl():
    def __init__(self):
        rospy.Subscriber('/publish_topic', TwistStamped, self.timestamp_callback, queue_size=10)
        self.timestamp_pub = rospy.Publisher('/subscribe_topic', TwistStamped, queue_size=10)

        # self.timestamp_msg = TwistStamped()
        
    def timestamp_callback(self, msg):
        self.timestamp_pub.publish(msg)

if __name__=='__main__':
    rospy.init_node("timestamp_ctl", anonymous=False)
    class_ctl = timestamp_ctl()

    rospy.spin()
