import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import serial
import math

class ObstacleAvoidanceNode(Node):
     def init(self):
         super().init('obstacle_avoidance_node')
         self.subscription = self.create_subscription(
             LaserScan,
             '/scan',
             self.laser_callback,
             10)
         self.publisher = self.create_publisher(String, '/motor_commands', 10)
         self.serial_connection = serial.Serial('/dev/ttyUSB0', 57600, timeout=2)

     def laser_callback(self, msg):
         ranges = msg.ranges
         min_distance = min(ranges)
         min_angle = ranges.index(min_distance)
         close = 0;

         if 0.20 <= min_distance < 0.30: 
             self.slowdown1()
         elif 0.10 <= min_distance < 0.20: 
             self.slowdown2()
         elif min_distance < 0.10:
             self.stop()
             if min_angle < len(ranges) / 2:
                self.rotate('right')
             else:
                self.rotate('left')
         else:
             self.forward()

     def slowdown1(self):
         self.send_command('o 175 175')

     def slowdown2(self):
         self.send_command('o 130 130')

     def stop(self):
         self.send_command('o 0 0')

     def forward(self):
         self.send_command('o 200 200')

     def rotate(self, direction):
         if direction == 'right':
            self.send_command('o 200 -200')
         else:
            self.send_command('o -200 200')

     def send_command(self, command):
         self.serial_connection.write((command + '\n').encode())
         self.get_logger().info('Sending command: ' + command)
         response = self.serial_connection.readline().decode().strip()
         self.get_logger().info('Received: ' + response)

 def main():
     rclpy.init()
     node = ObstacleAvoidanceNode()
     rclpy.spin(node)
     node.destroy_node()
     rclpy.shutdown()

if name == 'main':
main()