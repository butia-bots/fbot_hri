import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class EmotionsPublisher(Node):

    def __init__(self):
        super().__init__('emotions_publisher')
        self.publisher_ = self.create_publisher(String, 'fbot_face/emotion', 10)
        timer_period = 5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

        self.emotions = ['happy', 'sad', 'neutral', 'surprised', 'angry', 'suspicious', 'sleepy']

    def timer_callback(self):
        msg = String()
        msg.data = self.emotions[self.i]
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i = self.i+1 if self.i<6 else 0


def main(args=None):
    rclpy.init(args=args)

    emotions_publisher = EmotionsPublisher()

    rclpy.spin(emotions_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    emotions_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()