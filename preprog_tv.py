from gpiozero import LED, Button
import threading
import time

class DualElevatorArmSystem:
    def __init__(self):
        # X-Axis (Horizontal Arm)
        self.x_dir = LED(27)                                # GPIO27
        self.x_step = LED(22)                               # GPIO22

        self.x_home = Button(17, pull_up=True)              # GPIO17
        self.x_call = Button(4, pull_up=True)               # Shared call X position

        self.x_elev1_button5 = Button(18, pull_up=True)     # GPIO18
        self.x_elev2_button5 = Button(23, pull_up=True)     # GPIO23

        # Y-Axis (Vertical Arm)
        self.y_dir = LED(24)                                # GPIO24
        self.y_step = LED(25)                               # GPIO25

        self.y_home = Button(5, pull_up=True)               # GPIO5
        self.y_call = Button(6, pull_up=True)               # Shared call Y press depth

        self.y_elev1_button5 = Button(13, pull_up=True)     # GPIO13 (Elev1)
        self.y_elev2_button5 = Button(19, pull_up=True)     # GPIO19 (Elev2)

        self.step_delay = 0.0015
        self.running = True
        self.current_elevator = 1  # 1(left, smaller) or 2 (right, larger)

    def move_to_limit(self, axis, direction, limit_switch):
        dir_pin = self.x_dir if axis == 'x' else self.y_dir
        step_pin = self.x_step if axis == 'x' else self.y_step
        dir_pin.value = direction
        
        while not limit_switch.is_pressed and self.running:
            step_pin.on()
            time.sleep(self.step_delay)
            step_pin.off()
            time.sleep(self.step_delay)

    def home_all(self):
        def home(axis):
            dir_pin = self.x_dir if axis == 'x' else self.y_dir
            step_pin = self.x_step if axis == 'x' else self.y_step
            limit = self.x_home if axis == 'x' else self.y_home
            dir_pin.value = True  # Toward home
            
            while not limit.is_pressed and self.running:
                step_pin.on()
                time.sleep(self.step_delay)
                step_pin.off()
                time.sleep(self.step_delay)

        x_thread = threading.Thread(target=home, args=('x',))
        y_thread = threading.Thread(target=home, args=('y',))
        x_thread.start()
        y_thread.start()
        x_thread.join()
        y_thread.join()

    def press_button5(self):
        try:
            self.home_all()
            
            # Select current elevator's Button5 switches
            x_button5 = self.x_elev1_button5 if self.current_elevator == 1 else self.x_elev2_button5
            y_button5 = self.y_elev1_button5 if self.current_elevator == 1 else self.y_elev2_button5

            print(f"Pressing Elevator {self.current_elevator} Button 5...")
            x_thread = threading.Thread(
                target=self.move_to_limit,
                args=('x', False, x_button5)
            )
            y_thread = threading.Thread(
                target=self.move_to_limit,
                args=('y', False, y_button5)
            )
            x_thread.start()
            y_thread.start()
            x_thread.join()
            y_thread.join()

            time.sleep(1)  # Hold press
            self.home_all()

        except KeyboardInterrupt:
            self.running = False

    def press_call_button(self):
        try:
            self.home_all()
            print("Pressing Shared Call Button...")
            
            # Same X/Y for both elevators
            x_thread = threading.Thread(
                target=self.move_to_limit,
                args=('x', False, self.x_call)
            )
            y_thread = threading.Thread(
                target=self.move_to_limit,
                args=('y', False, self.y_call)
            )
            x_thread.start()
            y_thread.start()
            x_thread.join()
            y_thread.join()

            time.sleep(1)  # Hold press
            self.home_all()

        except KeyboardInterrupt:
            self.running = False

    def cleanup(self):
        self.running = False
        time.sleep(0.2)
        self.x_dir.close()
        self.x_step.close()
        self.y_dir.close()
        self.y_step.close()

if __name__ == "__main__":
    arms = DualElevatorArmSystem()
    try:
        while True:
            print(f"\nCurrent Elevator: {arms.current_elevator}")
            print("1. Switch Elevator")
            print("2. Home All")
            print("3. Press Button 5")
            print("4. Press Call Button")
            print("Q. Quit")
            
            choice = input("Select: ").lower()
            
            if choice == '1':
                arms.current_elevator = 2 if arms.current_elevator == 1 else 1
                print(f"Switched to Elevator {arms.current_elevator}")
            elif choice == '2':
                arms.home_all()
            elif choice == '3':
                arms.press_button5()
            elif choice == '4':
                arms.press_call_button()
            elif choice == 'q':
                break
    finally:
        arms.cleanup()
        print("System stopped")