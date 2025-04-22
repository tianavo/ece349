import rclpy
from gpiozero import LED
import time
from rclpy.node import Node
from sensor_msgs.msg import Joy

class Driver(Node):

    def __init__(self):
        super().__init__('driver_node')
        self.joy_sub = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        W1A_PIN = 17
        W1B_PIN = 18
        W2A_PIN = 22
        W2B_PIN = 23
        W3A_PIN = 19
        W3B_PIN = 16
        W4A_PIN = 26
        W4B_PIN = 20

        invert_w1 = True
        invert_w2 = True
        invert_w3 = True
        invert_w4 = True

        if invert_w1:
            self.W1A = LED(W1A_PIN)
            self.W1B = LED(W1B_PIN)
        else 
            self.W1A = LED(W1B_PIN)
            self.W1B = LED(W1A_PIN)

        if invert_w2:
            self.W2A = LED(W2A_PIN)
            self.W2B = LED(W2B_PIN)
        else
            self.W2A = LED(W2B_PIN)
            self.W2B = LED(W2A_PIN)

        if invert_w3:
            self.W3A = LED(W3A_PIN)
            self.W3B = LED(W3B_PIN)
        else
            self.W3A = LED(W3B_PIN)
            self.W3B = LED(W3A_PIN)

        if invert_w4:
            self.W4A = LED(W4A_PIN)
            self.W4B = LED(W4B_PIN)
        else
            self.W4A = LED(W4B_PIN)
            self.W4B = LED(W4A_PIN)

    def drive(self, mode):
        # mode: 
        # 1, 2, 3, 4, 5, 6
        # forward, backward, left, right, clockwise, counterclockwise
        match mode:
            case 1:
                self.W1A.on()
                self.W1B.off()
                self.W2A.on()
                self.W2B.off()
                self.W3A.on()
                self.W3B.off()
                self.W4A.on()
                self.W4B.off()
            case 2:
                self.W1A.off()
                self.W1B.on()
                self.W2A.off()
                self.W2B.on()
                self.W3A.off()
                self.W3B.on()
                self.W4A.off()
                self.W4B.on()
            case 3:
                self.W1A.off()
                self.W1B.on()
                self.W2A.on()
                self.W2B.off()
                self.W3A.off()
                self.W3B.on()
                self.W4A.on()
                self.W4B.off()
            case 4:
                self.W1A.on()
                self.W1B.off()
                self.W2A.off()
                self.W2B.on()
                self.W3A.on()
                self.W3B.off()
                self.W4A.off()
                self.W4B.on()
            case 5:
                self.W1A.off()
                self.W1B.on()
                self.W2A.on()
                self.W2B.off()
                self.W3A.on()
                self.W3B.off()
                self.W4A.off()
                self.W4B.on()
            case 6:
                self.W1A.on()
                self.W1B.off()
                self.W2A.off()
                self.W2B.on()
                self.W3A.off()
                self.W3B.on()
                self.W4A.on()
                self.W4B.off()
            case _:
                self.W1A.off()
                self.W1B.off()
                self.W2A.off()
                self.W2B.off()
                self.W3A.off()
                self.W3B.off()
                self.W4A.off()
                self.W4B.off()

    def listener_callback(self, msg):
        if msg.axes[5] > 0:
            drive(1)
        elif msg.axes[5] < 0:
            drive(2)
        elif msg.axes[4] > 0:
            drive(3)
        elif msg.axes[4] < 0:
            drive(4)
        elif msg.button[4] < 0:
            drive(5)
        elif msg.button[5] < 0:
            drive(6)
        else
            drive(0)

def main(args=None):
    rclpy.init(args=args)

    driver = Driver()

    rclpy.spin(driver)

    driver.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
