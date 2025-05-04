#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import time
import threading
from gpiozero import LED, Button

# --- GPIO Setup ---
DIRX = 27  # Horizontal: left/right
PULX = 22
DIRY = 24  # Vertical: up/down
PULY = 25
LIMIT_X = 5  # X-axis limit switch
LIMIT_Y = 6  # Y-axis limit switch

# Initialize GPIO
dirX = LED(DIRX)
pulX = LED(PULX)
dirY = LED(DIRY)
pulY = LED(PULY)
limit_switch_x = Button(LIMIT_X, pull_up=True)
limit_switch_y = Button(LIMIT_Y, pull_up=True)

class GantryController(Node):
    def __init__(self):
        super().__init__('gantry_controller')
        self.target_x = 300  # steps
        self.target_y = 200  # steps
        self.step_delay = 0.0015
        self.get_logger().info("Gantry Controller with GPIO initialized")

    def step_motor(self, dir_pin, pul_pin, direction, steps):
        """Perform motor steps in a given direction"""
        dir_pin.on() if direction else dir_pin.off()

        for _ in range(steps):
            pul_pin.on()
            time.sleep(self.step_delay)
            pul_pin.off()
            time.sleep(self.step_delay)

    def move_to_position(self, x_steps, y_steps):
        """Move gantry to position with threading using GPIO"""
        def move_axis(axis, steps, direction):
            if axis == 'x':
                dir_pin = dirX
                pul_pin = pulX
                dir_val = (direction == 'right')
            else:
                dir_pin = dirY
                pul_pin = pulY
                dir_val = (direction == 'up')

            self.step_motor(dir_pin, pul_pin, dir_val, steps)

        x_dir = 'right' if x_steps >= 0 else 'left'
        y_dir = 'up' if y_steps >= 0 else 'down'

        thread_x = threading.Thread(target=move_axis, args=('x', abs(x_steps), x_dir))
        thread_y = threading.Thread(target=move_axis, args=('y', abs(y_steps), y_dir))

        thread_x.start()
        thread_y.start()

        thread_x.join()
        thread_y.join()

        self.get_logger().info(f"Movement completed to X:{x_steps}, Y:{y_steps}")

    def home_gantry(self):
        """Home both axes using limit switches"""
        def home_axis(axis):
            if axis == 'x':
                dir_pin = dirX
                pul_pin = pulX
                limit_switch = limit_switch_x
                dir_pin.off()  # Assuming off is toward limit switch (left)
            else:
                dir_pin = dirY
                pul_pin = pulY
                limit_switch = limit_switch_y
                dir_pin.off()  # Assuming off is toward limit switch (down)

            self.get_logger().info(f"Homing {axis}-axis...")

            while not limit_switch.is_pressed:
                pul_pin.on()
                time.sleep(self.step_delay)
                pul_pin.off()
                time.sleep(self.step_delay)

            self.get_logger().info(f"{axis}-axis homed.")

        thread_x = threading.Thread(target=home_axis, args=('x',))
        thread_y = threading.Thread(target=home_axis, args=('y',))

        thread_x.start()
        thread_y.start()
        thread_x.join()
        thread_y.join()

        self.get_logger().info("Homing completed")

    def execute_button_press_sequence(self):
        """Run movement to button then home"""
        try:
            self.move_to_position(self.target_x, self.target_y)
            # Optionally: add a delay or GPIO signal to "press" the button here
            self.home_gantry()
        except Exception as e:
            self.get_logger().error(f"Error in sequence: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    controller = GantryController()
    controller.execute_button_press_sequence()
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
