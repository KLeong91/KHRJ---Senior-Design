#!/usr/bin/env python3


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.duration import Duration

class motor_control_test(Node):
    def __init__(self):
        super().__init__('motor_control_test')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.start_time = self.get_clock().now()
        self.actions = ['forward', 'rotate_left', 'stop', 'rotate_right', 'stop_end']
        self.action_index = 0
        self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        current_time = self.get_clock().now()
        elapsed_time = current_time - self.start_time

        twist = Twist()

        if elapsed_time < Duration(seconds=3):
            if self.actions[self.action_index] == 'forward':
                twist.linear.x = 0.5
            elif self.actions[self.action_index] == 'rotate_left':
                twist.angular.z = 0.5
            elif self.actions[self.action_index] == 'rotate_right':
                twist.angular.z = -0.5
        else:
            self.action_index += 1
            if self.action_index >= len(self.actions):
                self.destroy_node()
                return
            self.start_time = self.get_clock().now()

        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = motor_control_test()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
