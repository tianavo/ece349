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
from gpiozero import LED
import time
from rclpy.node import Node

from geometry_msgs.msg import Point


class Gantry(Node):

    def __init__(self):
        super().__init__('gantry_node')
        self.subscription = self.create_subscription(
            Point,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        DIRX = 27
        PULX = 22

        DIRY = 24
        PULY = 25

        self.dirX = LED(DIRX)
        self.dirY = LED(DIRY)
        self.pulX = LED(PULX)
        self.pulY = LED(PULY)
        self.delay = 0.002

    def listener_callback(self, msg):
        #curr_step = 0
        if msg.x > 0:
            self.dirX.on()
            self.dirY.on()
        else:
            self.dirX.off()
            self.dirY.off()

        steps = int(msg.z)

        if msg.y > 0:
            for _ in range(steps):
            #while True:
                #self.get_logger().info('"%i"' % curr_step)
                #curr_step = curr_step+1
                self.pulX.on()
                time.sleep(self.delay)
                self.pulX.off()
                time.sleep(self.delay)
        else:
            for _ in range(steps):
                self.pulY.on()
                time.sleep(self.delay)
                self.pulY.off()
                time.sleep(self.delay)



def main(args=None):
    rclpy.init(args=args)

    gantry = Gantry()

    rclpy.spin(gantry)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    gantry.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
