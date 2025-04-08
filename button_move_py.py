from gpiozero import LED
import time

# Define GPIO pins
DIRX = 27  # Used for horizontal movement: left/right
PULX = 22

DIRY = 24  # Used for vertical movement: up/down
PULY = 25

# Initialize control pins
dirX = LED(DIRX)
dirY = LED(DIRY)
pulX = LED(PULX)
pulY = LED(PULY)

# Movement, where delay = speed but there is a limit (cannot move too fast)
# 1000 steps = 1 inch IRL
def move_stepper(pul_pin, direction_pin, steps, delay=0.0015):
    direction_pin.on()
    for _ in range(steps):
        pul_pin.on()
        time.sleep(delay)
        pul_pin.off()
        time.sleep(delay)
    direction_pin.off()

# Movement logic based on axis and direction given in function
def move_axis(axis, direction, steps):
    if axis == 'x':  # Horizontal
        pul_pin = pulX
        if direction == 'right':
            direction_pin = dirY
        elif direction == 'left':
            direction_pin = dirX
        else:
            raise ValueError("Invalid horizontal direction. Use 'left' or 'right'.")
    elif axis == 'y':  # Vertical
        pul_pin = pulY
        if direction == 'down':
            direction_pin = dirY
        elif direction == 'up':
            direction_pin = dirX
        else:
            raise ValueError("Invalid vertical direction. Use 'up' or 'down'.")
    else:
        raise ValueError("Axis must be 'x' or 'y'")

    move_stepper(pul_pin, direction_pin, steps)

# Home position
def home_position():
    print("Already at home position. No movement required.")

# Call elevator
def call_elevator():
    print("Calling elevator...")
    move_axis('x', 'right', 500) # Change values of steps for accuracy
    move_axis('y', 'down', 650)  # 1000 steps = 1 inch
    print("Returning to home...")
    move_axis('y', 'up', 650)
    move_axis('x', 'left', 500)

# Elevator 1 (left, smaller), Button 5
def press_elevator1_button_5():
    print("Pressing Elevator 1 - Button 5...")
    move_axis('x', 'right', 600)
    move_axis('y', 'down', 700)
    print("Returning to home...")
    move_axis('y', 'up', 700)
    move_axis('x', 'left', 600)

# Elevator 2 (right, larger), Button 5
def press_elevator2_button_5():
    print("Pressing Elevator 2 - Button 5...")
    move_axis('x', 'right', 800)
    move_axis('y', 'down', 750)
    print("Returning to home...")
    move_axis('y', 'up', 750)
    move_axis('x', 'left', 800)

# Test sequence
if __name__ == "__main__":
    home_position()
    time.sleep(1)
    call_elevator()
    time.sleep(1)
    press_elevator1_button_5()
    time.sleep(1)
    press_elevator2_button_5()
    time.sleep(1)
    home_position()