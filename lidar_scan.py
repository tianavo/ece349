#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import numpy as np

class LidarDoorDetector(Node):
    def __init__(self):
        super().__init__('lidar_door_detector')
        
        # Subscriber
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',  # Your LIDAR topic
            self.lidar_callback,
            10)
        
        # Publisher for door status
        self.door_pub = self.create_publisher(Bool, '/door_status', 10)
        
        # Detection parameters
        self.detection_angle = 0.0  # Center angle (radians) (0=straight ahead)
        self.angle_range = np.pi/8  # ±22.5 degree range to monitor
        self.distance_threshold = 1.0  # 1 meter increase threshold
        self.min_initial_distance = 0.5  # Minimum valid initial distance (meters)
        
        # State variables
        self.initial_distance = None
        self.door_open = False
        self.stable_readings = 0
        self.required_stable_readings = 3  # Require 3 consistent readings
        
        self.get_logger().info("LIDAR Door Detector initialized")

    def lidar_callback(self, msg):
        """Process LIDAR data and detect door openings"""
        try:
            # Get indices for our detection angle range
            angle_min = msg.angle_min
            angle_inc = msg.angle_increment
            center_idx = int((self.detection_angle - angle_min) / angle_inc)
            range_idx = int(self.angle_range / angle_inc)
            
            start_idx = max(0, center_idx - range_idx)
            end_idx = min(len(msg.ranges), center_idx + range_idx)
            
            # Extract ranges in our detection zone (convert 0's to inf)
            ranges = np.array(msg.ranges)
            ranges[ranges == 0] = np.inf
            
            # Calculate median distance in detection zone
            current_distance = np.median(ranges[start_idx:end_idx])
            
            # Initialize or update baseline distance
            if self.initial_distance is None:
                if current_distance < np.inf and current_distance > self.min_initial_distance:
                    self.initial_distance = current_distance
                    self.get_logger().info(f"Initial distance set to: {self.initial_distance:.2f}m")
                return
            
            # Check for significant distance increase
            if current_distance > (self.initial_distance + self.distance_threshold):
                self.stable_readings += 1
                if not self.door_open and self.stable_readings >= self.required_stable_readings:
                    self.door_open = True
                    self.get_logger().info(f"Door OPEN detected! Current distance: {current_distance:.2f}m")
            else:
                self.stable_readings = max(0, self.stable_readings - 1)
                if self.door_open and self.stable_readings == 0:
                    self.door_open = False
                    self.get_logger().info(f"Door CLOSED detected. Current distance: {current_distance:.2f}m")
            
            # Publish door status
            status = Bool()
            status.data = self.door_open
            self.door_pub.publish(status)
            
        except Exception as e:
            self.get_logger().error(f"Error processing LIDAR data: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LidarDoorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()