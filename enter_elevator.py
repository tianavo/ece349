#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from apriltag_msgs.msg import AprilTagDetectionArray
from gpiozero import LED
import time
import numpy as np

class ElevatorEntryController(Node):
    def __init__(self):
        super().__init__('elevator_entry_controller')
        
        # Motor control (same as your original)
        self.W1A = LED(17)  # No inversion
        self.W1B = LED(18)
        self.W2A = LED(22)  # No inversion
        self.W2B = LED(23)
        self.W3A = LED(16)  # INVERTED (per your invert_w3=True)
        self.W3B = LED(19)
        self.W4A = LED(26)  # No inversion
        self.W4B = LED(20)
        
        # Subscriptions
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10)
        
        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            '/apriltag_detections',
            self.tag_callback,
            10)
        
        # State variables
        self.state = "WAIT_FOR_DOOR"  # WAIT_FOR_DOOR, MOVE_FORWARD, TURN_CLOCKWISE, SHIFT_RIGHT, STOPPED
        self.target_tag_id = 0
        self.initial_distance = None
        self.action_start_time = None
        
        # Timing parameters (seconds)
        self.turn_duration = 2.0    # Clockwise turn time
        self.shift_duration = 1.5   # Right shift time
        
        #self.get_logger().info("Controller ready - will perform full maneuver sequence")

    def lidar_callback(self, msg):
        """Handle door opening detection"""
        if self.state != "WAIT_FOR_DOOR":
            return
            
        # Focus on front-facing beams (90° ± 15°)
        center_idx = len(msg.ranges) // 2
        start_idx = max(0, center_idx - int(15 / np.degrees(msg.angle_increment)))
        end_idx = min(len(msg.ranges), center_idx + int(15 / np.degrees(msg.angle_increment)))
        
        valid_ranges = [r for r in msg.ranges[start_idx:end_idx] if not np.isinf(r)]
        if not valid_ranges:
            return
            
        current_distance = np.median(valid_ranges)
        
        if self.initial_distance is None:
            self.initial_distance = current_distance
            return
            
        if current_distance > self.initial_distance + 0.2:  # 20cm threshold
            self.state = "MOVE_FORWARD"
            self.move_forward()
            #self.get_logger().info("Door opened - moving forward")

    def tag_callback(self, msg):
        """Handle AprilTag detections"""
        if self.state != "MOVE_FORWARD":
            return
            
        for detection in msg.detections:
            if detection.id == self.target_tag_id:
                #self.get_logger().info(f"Detected tag ID {self.target_tag_id} - beginning maneuver")
                self.state = "TURN_CLOCKWISE"
                self.action_start_time = time.time()
                self.turn_clockwise()
                break

    def execute_maneuver(self):
        """Handle ongoing maneuvers"""
        if self.state == "TURN_CLOCKWISE":
            if time.time() - self.action_start_time >= self.turn_duration:
                self.state = "SHIFT_RIGHT"
                self.action_start_time = time.time()
                self.shift_right()
                self.get_logger().info("Turn complete - shifting right")
                
        elif self.state == "SHIFT_RIGHT":
            if time.time() - self.action_start_time >= self.shift_duration:
                self.state = "STOPPED"
                self.stop()
                self.get_logger().info("Maneuver complete - stopped")

    def move_forward(self):
        """Case 1: Forward movement"""
        self.W1A.on()
        self.W1B.off()
        self.W2A.on()
        self.W2B.off()
        self.W3A.on()
        self.W3B.off()
        self.W4A.on()
        self.W4B.off()

    def turn_clockwise(self):
        """Case 5: Clockwise turn (right rotation in place)"""
        self.W1A.off()
        self.W1B.on()
        self.W2A.on()
        self.W2B.off()
        self.W3A.on()
        self.W3B.off()
        self.W4A.off()
        self.W4B.on()

    def shift_right(self):
        """Case 4: Rightward shift"""
        self.W1A.on()
        self.W1B.off()
        self.W2A.off()
        self.W2B.on()
        self.W3A.on()
        self.W3B.off()
        self.W4A.off()
        self.W4B.on()

    def stop(self):
        """Stop all motors"""
        self.W1A.off()
        self.W1B.off()
        self.W2A.off()
        self.W2B.off()
        self.W3A.off()
        self.W3B.off()
        self.W4A.off()
        self.W4B.off()

    def timer_callback(self):
        """Handle timed maneuvers"""
        self.execute_maneuver()

def main(args=None):
    rclpy.init(args=args)
    node = ElevatorEntryController()
    
    # Create timer for maneuver execution (10Hz)
    node.create_timer(0.1, node.timer_callback)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()