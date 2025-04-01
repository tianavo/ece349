# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Point

class ButtonMovementTranslator(Node):
    def __init__(self):
        super().__init__('button_movement_translator')
        
        # publisher to send movement commands to the gantry
        self.gantry_pub = self.create_publisher(Point, 'topic', 10)
        
        # service to handle button press requests
        self.srv = self.create_service(
            ButtonPress, 
            'button_press_service',
            self.button_press_callback)
        
        # preprogrammed button positions (need to be measured in the physical elevator environment)
        # format: {floor_number: {'x': x_steps, 'y': y_steps}}
        self.button_positions = {
            2: {'x': 100, 'y': 50},    # EXAMPLE VALUES - MUST BE MEASURED
            3: {'x': 120, 'y': 75},    # x = horizontal steps, y = vertical steps
            4: {'x': 140, 'y': 100},   # Negative values would move in opposite direction
            5: {'x': 160, 'y': 125},   
            6: {'x': 180, 'y': 150}    
        }
        
        self.get_logger().info("Button Movement Translator Ready")

    def button_press_callback(self, request, response):
        """Handle requests to press specific buttons"""
        floor = request.floor_number
        self.get_logger().info(f"Received request for floor {floor}")
        
        if floor not in self.button_positions:
            response.success = False
            response.message = f"Floor {floor} not configured"
            return response
        
        # get preprogrammed movement values
        movement = self.button_positions[floor]
        
        # first move horizontally (X axis)
        self.move_axis(x=1.0, y=0.0, steps=movement['x'])
        
        # then move vertically (Y axis)
        self.move_axis(x=0.0, y=1.0, steps=movement['y'])
        
        # return to home position (might want this)
        # self.return_to_home()
        
        response.success = True
        response.message = f"Button {floor} pressed successfully"
        return response

    def move_axis(self, x, y, steps):
        """Helper function to send movement commands to gantry"""
        msg = Point()
        msg.x = float(x)  # direction (1.0 or -1.0)
        msg.y = float(y)  # axis selection (1.0 = X, 0.0 = Y)
        msg.z = float(steps)  # num of steps
        
        self.gantry_pub.publish(msg)
        self.get_logger().info(f"Sent command: {msg}")
        time.sleep(0.1)  # small delay

    def return_to_home(self):
        """return to home position"""
        # this would need to be calibrated with your actual home position steps
        self.get_logger().info("Returning to home position")
        # move Y axis up (example - adjust direction and steps as needed)
        self.move_axis(x=0.0, y=1.0, steps=200)  # need to be calculated
        # move X axis left (example)
        self.move_axis(x=-1.0, y=0.0, steps=200)  # need to be calculated


def main(args=None):
    rclpy.init(args=args)
    translator = ButtonMovementTranslator()
    rclpy.spin(translator)
    translator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()