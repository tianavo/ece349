from gpiozero import LED, Button
import time
import threading

# Define GPIO pins
DIRX = 27
PULX = 22
DIRY = 24
PULY = 25

# Limit switch GPIO pins (update if needed)
LIMIT_X = 5
LIMIT_Y = 6

# Initialize motor control pins
dirX = LED(DIRX)
dirY = LED(DIRY)
pulX = LED(PULX)
pulY = LED(PULY)

# Initialize limit switches (Normally Open to GND, Common to GPIO)
limit_switch_x = Button(LIMIT_X, pull_up=True)
limit_switch_y = Button(LIMIT_Y, pull_up=True)

# Generic stepper movement function
def move_stepper(pul_pin, direction_pin, steps, delay=0.0015):
    direction_pin.on()
    for _ in range(steps):
        pul_pin.on()
        time.sleep(delay)
        pul_pin.off()
        time.sleep(delay)
    direction_pin.off()

# Move along X or Y axis
def move_axis(axis, direction, steps, delay=0.0015):
    if axis == 'x':
        pul_pin = pulX
        direction_pin = dirY if direction == 'right' else dirX
    elif axis == 'y':
        pul_pin = pulY
        direction_pin = dirY if direction == 'down' else dirX
    else:
        raise ValueError("Axis must be 'x' or 'y'")

    move_stepper(pul_pin, direction_pin, steps, delay)

# Homing function using limit switches
def home_with_limit(axis, direction, delay=0.0015):
    print(f"Homing {axis.upper()}-axis toward {direction}...")
    
    if axis == 'x':
        pul_pin = pulX
        dir_pin = dirY if direction == 'right' else dirX
        limit_switch = limit_switch_x
    elif axis == 'y':
        pul_pin = pulY
        dir_pin = dirY if direction == 'down' else dirX
        limit_switch = limit_switch_y
    else:
        raise ValueError("Axis must be 'x' or 'y'")

    dir_pin.on()
    while not limit_switch.is_pressed:
        pul_pin.on()
        time.sleep(delay)
        pul_pin.off()
        time.sleep(delay)
    dir_pin.off()

    print(f"{axis.upper()}-axis homed.")

# Combined home sequence
def home_all():
    home_with_limit('x', 'left')
    time.sleep(0.5)
    home_with_limit('y', 'up')
    time.sleep(0.5)

# Move both axes at the same time using threading
def move_axes_simultaneously(x_direction, y_direction, x_steps, y_steps, delay=0.0015):
    # Create threads for simultaneous movement
    thread_x = threading.Thread(target=move_axis, args=('x', x_direction, x_steps, delay))
    thread_y = threading.Thread(target=move_axis, args=('y', y_direction, y_steps, delay))

    # Start both threads
    thread_x.start()
    thread_y.start()

    # Wait for both threads to finish
    thread_x.join()
    thread_y.join()

# Go to elevator position (starts with homing)
def call_elevator():
    print("Calling elevator...")
    home_all()
    move_axes_simultaneously('right', 'down', 500, 650)

# Elevator 1 button press
def press_elevator1_button_5():
    print("Pressing Elevator 1 - Button 5...")
    home_all()
    move_axes_simultaneously('right', 'down', 600, 700)

# Elevator 2 button press
def press_elevator2_button_5():
    print("Pressing Elevator 2 - Button 5...")
    home_all()
    move_axes_simultaneously('right', 'down', 800, 750)

# Go back to home anytime
def return_home():
    print("Returning to home...")
    home_all()

# Test routine
if __name__ == "__main__":
    home_all()
    time.sleep(1)
    call_elevator()
    time.sleep(1)
    return_home()
    time.sleep(1)
    press_elevator1_button_5()
    time.sleep(1)
    return_home()
    time.sleep(1)
    press_elevator2_button_5()
    time.sleep(1)
    return_home()