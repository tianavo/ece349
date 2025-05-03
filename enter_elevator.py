#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from gpiozero import LED
import time
import numpy as np

class ElevatorEntryController(Node):
    def __init__(self):
        super().__init__('elevator_entry_controller')
        
        # Motor control
        self.W1A = LED(17)  # No inversion
        self.W1B = LED(18)
        self.W2A = LED(22)  # No inversion
        self.W2B = LED(23)
        self.W3A = LED(16)  # INVERTED (per your invert_w3=True)
        self.W3B = LED(19)
        self.W4A = LED(26)  # No inversion
        self.W4B = LED(20)
        
        # LIDAR subscription
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10)
        
        # State variables
        self.initial_distance = None
        self.door_opening_detected = False
        self.movement_start_time = None
        
        self.get_logger().info("Elevator entry controller ready. Waiting for door opening...")

    def lidar_callback(self, msg):
        # Focus on front-facing beams (90° ± 15°)
        center_idx = len(msg.ranges) // 2
        start_idx = max(0, center_idx - int(15 / np.degrees(msg.angle_increment)))
        end_idx = min(len(msg.ranges), center_idx + int(15 / np.degrees(msg.angle_increment)))
        
        valid_ranges = [r for r in msg.ranges[start_idx:end_idx] if not np.isinf(r)]
        if not valid_ranges:
            return
            
        current_distance = np.median(valid_ranges)
        
        # First measurement sets the baseline
        if self.initial_distance is None:
            self.initial_distance = current_distance
            self.get_logger().info(f"Initial door distance set to: {self.initial_distance:.2f}m")
            return
            
        # Check for door opening (distance increase)
        if not self.door_opening_detected and current_distance > self.initial_distance + 0.2:  # 20cm threshold
            self.door_opening_detected = True
            self.movement_start_time = time.time()
            self.move_forward()
            self.get_logger().info("Door opening detected! Moving forward for 2 seconds")
            
        # Check if 2 seconds have passed
        if self.door_opening_detected and time.time() - self.movement_start_time >= 2.0:
            self.stop()
            self.door_opening_detected = False
            self.initial_distance = None  # Reset for next use
            self.get_logger().info("Movement complete. Ready for next operation.")

    def move_forward(self):
        """Activate motors for forward movement (your case 1)"""
        self.W1A.on()
        self.W1B.off()
        self.W2A.on()
        self.W2B.off()
        self.W3A.on()
        self.W3B.off()
        self.W4A.on()
        self.W4B.off()

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

def main(args=None):
    rclpy.init(args=args)
    node = ElevatorEntryController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop()  # Ensure motors stop on shutdown
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()