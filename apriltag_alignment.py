#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Int32
import math

class AprilTagAligner(Node):
    def __init__(self):
        super().__init__('apriltag_aligner')
        
        # TF2 setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Publisher for your driver commands
        self.drive_pub = self.create_publisher(Int32, '/drive_command', 10)
        
        # Alignment parameters
        self.linear_threshold = 0.1  # meters
        self.angular_threshold = 0.2  # radians
        
        # Control parameters
        self.alignment_active = False
        self.current_tag_id = None
        
        # Main control loop (10Hz)
        self.timer = self.create_timer(0.1, self.control_loop)

    def get_tag_pose(self):
        """Check for any AprilTag transform"""
        try:
            # Get all available transforms
            transforms = self.tf_buffer.all_frames_as_yaml()
            
            # Find the first AprilTag transform
            for frame in transforms.split('\n'):
                if 'tag36h11:' in frame:
                    tag_id = frame.split(':')[1].strip()
                    transform = self.tf_buffer.lookup_transform(
                        'camera_frame',
                        f'tag36h11:{tag_id}',
                        rclpy.time.Time())
                    return transform, tag_id
            return None, None
        except TransformException as ex:
            self.get_logger().warn(f'TF error: {ex}')
            return None, None

    def control_loop(self):
        """Main alignment control loop"""
        transform, tag_id = self.get_tag_pose()
        
        if not transform:
            if self.alignment_active:
                self.get_logger().info("Lost AprilTag detection")
                self.stop_movement()
                self.alignment_active = False
                self.current_tag_id = None
            return
        
        # If we found a new tag, note its ID
        if not self.alignment_active:
            self.current_tag_id = tag_id
            self.get_logger().info(f"Detected AprilTag {tag_id}, beginning alignment")
            self.alignment_active = True
        
        # Get translation and rotation
        trans = transform.transform.translation
        rot = transform.transform.rotation
        
        cmd = Int32()
        aligned = True
        
        # X-axis alignment (left/right movement)
        if abs(trans.x) > self.linear_threshold:
            aligned = False
            if trans.x > self.linear_threshold:
                cmd.data = 4  # Right (from your driver_node)
                self.get_logger().info("Adjusting RIGHT")
            else:
                cmd.data = 3  # Left (from your driver_node)
                self.get_logger().info("Adjusting LEFT")
            self.drive_pub.publish(cmd)
            return
        
        # Y-axis alignment (forward/backward movement)
        if abs(trans.y) > self.linear_threshold:
            aligned = False
            if trans.y > self.linear_threshold:
                cmd.data = 1  # Forward
                self.get_logger().info("Adjusting FORWARD")
            else:
                cmd.data = 2  # Backward
                self.get_logger().info("Adjusting BACKWARD")
            self.drive_pub.publish(cmd)
            return
        
        # Rotation alignment (only checking y-axis for downward facing)
        if abs(rot.y + 1.0) > self.angular_threshold:  # Target is y=-1
            aligned = False
            if rot.y < -1.0:
                cmd.data = 5  # Clockwise
                self.get_logger().info("Rotating CLOCKWISE")
            else:
                cmd.data = 6  # Counter-clockwise
                self.get_logger().info("Rotating COUNTER-CLOCKWISE")
            self.drive_pub.publish(cmd)
            return
        
        if aligned:
            self.get_logger().info(f"Perfectly aligned with AprilTag {self.current_tag_id}!")
            self.stop_movement()
            self.alignment_active = False

    def stop_movement(self):
        """Stop all movement"""
        cmd = Int32()
        cmd.data = 0
        self.drive_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = AprilTagAligner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()