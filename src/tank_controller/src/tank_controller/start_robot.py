#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist  # Import Twist message type
from std_msgs.msg import String
import math
import time

object_detected = False
object = ""
object_direction = ""

pass1 = False
pass2 = False
pass3 = False

class ObstacleAvoidanceNode(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance_node')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)  # Publish to /cmd_vel
        self.arm_publisher = self.create_publisher(String, 'activation_signal', 10)
        self.object_subscriber = self.create_subscription(String, 'object_info', self.image_callback, 10)
        self.joy_subscription = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.robot_automatic = True
        self.last_button_press_time = None
        self.timer_duration = 8  # 8 seconds
        self.middle_button_prev_state = False  # Initialize previous state of middle button
    
    def joy_callback(self, data):

        # If middle button is released, make it manual mode
        if data.buttons[10] == 0 and self.middle_button_prev_state:
            self.robot_automatic = not self.robot_automatic
            self.stop()

        # Update previous state of middle button
        self.middle_button_prev_state = bool(data.buttons[10])
        
        # If we are in manual mode
        if not self.robot_automatic:
            # Right trigger = forward
            if data.buttons[7] > 0:  
                self.forward(2.0)

            # Left trigger = backward
            elif data.buttons[6] > 0:  
                self.reverse(-2.0)
            else:
                self.stop()

            # Left joystick = rotation
            if data.axes[0] < -.2:
                self.rotate("right", -1.0)
            elif data.axes[0] > .2:
                self.rotate("left", 1.0)

            # Activate arm for recycle
            if data.buttons[0] > 0:
                msg = String()
                msg.data = "activate_recycle"
                self.arm_publisher.publish(msg) 
                time.sleep(1)
                
            # Check if the O button is pressed
            if data.buttons[1] > 0:
                msg = String()
                msg.data = "activate_compost"
                self.arm_publisher.publish(msg) 
                time.sleep(1)
               
    def image_callback(self, msg):
        global object_detected, object, object_direction
        object_detected = True
        object_data = msg.data

        object = object_data.split()[0]
        object_coordinates = object_data.split()[1] + ", " + object_data.split()[2]

        if int(object_data.split()[1]) > 0:
            object_direction = "right"
        else:
            object_direction = "left"
            

        self.get_logger().info(f"Found {object} at {object_coordinates}")
        print(f"Found {object} at {object_coordinates}")
        

    def laser_callback(self, msg):
 
        global object_detected, object, object_direction, pass1, pass2, pass3

        if self.robot_automatic:

            # Define the width of your field of view in radians
            fov = 100  # 180 degrees

            # Find the range of indices to consider
            # The width of the field of view is evenly divided around the central index
            start_index = math.floor((len(msg.ranges) / 2) - (fov / 2))
            end_index = math.ceil((len(msg.ranges) / 2) + (fov / 2))

            # Get the range values within the defined range of indices
            ranges_in_fov = msg.ranges[start_index:end_index + 1]  # Add 1 to end_index to include the last index

            # Calculate the distance to the nearest object in front of the sensor
            # Use the minimum range value within the field of view
            min_distance = min(ranges_in_fov)
            obstacle_angle = (start_index + ranges_in_fov.index(min_distance)) * (fov / len(msg.ranges)) - fov / 2

            # Print the distance to the nearest object in front of the sensor
            print(f"Distance to nearest object: {min_distance:.2f} meters") 

            if object_detected:
                # Move forward until feasable distance
                if (pass1 == False):
                    print("MOVE FORWARD first")
                    if (min_distance >= .9):
                        self.forward()
                        return
                    else:
                        print("PASS 1 DONE")
                        pass1 = True
                # Rotate until centered
                if (pass2 == False):
                    print("We are at pass 2 now")
                    print(f"object direction is {object_direction}")
                    print(f"obstacle angle is {obstacle_angle}")
                    if object_direction == 'right':
                        if (obstacle_angle <= -1.4): 
                            self.rotate('right', -.1)
                            print("obstacle_angle: ")
                            print(obstacle_angle)
                            print("ROTATE RIGHT")
                            return
                        elif not (obstacle_angle >= 5):
                            pass2 = True
                    if object_direction == 'left':
                        if (obstacle_angle >= 1.5): 
                            self.rotate('left', .1)
                            print("ROTATE LEFT")
                            return
                        elif not (obstacle_angle <= -5):
                            pass2 = True
                #Move 
                if (pass3 == False):
                    if (min_distance >= .27):
                        if (min_distance <= 1.0):
                            self.slowdown2()                
                        print("min_distance: ")
                        print(min_distance)
                        print("MOVE FORWARD second")
                        return
                    else:
                        # Activate arm
                        print("activate arm")
                        msg = String()
                        msg.data = "activate_recycle"
                        self.arm_publisher.publish(msg) 
                        time.sleep(3.5)
                        self.slowdown2()
                        time.sleep(.5)
                        self.stop()
                        time.sleep(5)
                        object_detected = False
                        pass1 = False
                        pass2 = False
                        pass3 = False

            # Determine actions based on the minimum distance to an obstacle
            if 0.3 <= min_distance < 0.35:
                print("its slow")
                self.slowdown1()
            elif 0.25 <= min_distance < 0.3:
                print("its slower")
                self.slowdown2()
            elif min_distance < 0.25:
                print("its stopped")
                self.stop()
                # Decide direction based on the position of the closest obstacle in the right half
                print("obstacle angle: ")
                print(obstacle_angle)
                if obstacle_angle > 0:
                    print("object is to the left")
                    self.rotate('right', -2.0)  # Obstacle is more to the "front-right"
                else:
                    print("object is to the right")
                    self.rotate('left', 2.0)  # Obstacle is more to the "back-right"
            else:
                self.forward(1.3)

    def slowdown1(self):
        twist = Twist()
        twist.linear.x = 0.175  # Slow forward speed
        self.publisher.publish(twist)

    def slowdown2(self):
        twist = Twist()
        twist.linear.x = 0.130  # Slower forward speed
        self.publisher.publish(twist)

    def stop(self):
        twist = Twist()  # Stop movement
        twist.linear.x = 0.0  
        twist.angular.z = 0.0
        self.publisher.publish(twist)

    def forward(self, speed):
        twist = Twist()
        twist.linear.x = speed  # Forward speed
        self.publisher.publish(twist)

    def reverse(self, speed):
        twist = Twist()
        twist.linear.x = speed  # Forward speed
        self.publisher.publish(twist)

    def rotate(self, direction, speed):
        twist = Twist()
        if direction == 'right':
            twist.angular.z = speed  # Rotate right
        else:
            twist.angular.z = speed  # Rotate left
        self.publisher.publish(twist)

def main():
    rclpy.init()
    node = ObstacleAvoidanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
