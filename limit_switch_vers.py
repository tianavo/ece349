from gpiozero import LED, Button
import serial
import struct
import time
import threading

# --- GPIO Setup ---
DIRX = 27  # Horizontal: left/right
PULX = 22
DIRY = 24  # Vertical: up/down
PULY = 25
LIMIT_X = 5  # X-axis limit switch
LIMIT_Y = 6  # Y-axis limit switch

# Initialize GPIO
dirX = LED(DIRX)
dirY = LED(DIRY)
pulX = LED(PULX)
pulY = LED(PULY)
limit_switch_x = Button(LIMIT_X, pull_up=True)
limit_switch_y = Button(LIMIT_Y, pull_up=True)

# --- LiDAR Configuration ---
PORT = "/dev/ttyUSB0"
BAUDRATE = 230400
LEFT_ANGLE = 45.0    # Adjustable
RIGHT_ANGLE = 315.0
THRESHOLD = 500          # mm change to detect door opening
BASELINE_LEFT = 1000     # Measure with doors closed
BASELINE_RIGHT = 1000    # 1000m = 1m ~ 3ft

# --- Stepper Control Functions ---
def move_stepper(pul_pin, direction_pin, steps, delay=0.0015): # maybe 0.0013 for slightly faster speed
    """Core stepper movement function"""
    direction_pin.on()
    for _ in range(steps):
        pul_pin.on()
        time.sleep(delay)
        pul_pin.off()
        time.sleep(delay)
    direction_pin.off()

def move_axis(axis, direction, steps, delay=0.0015):
    """Move specified axis in direction"""
    if axis == 'x':
        pul_pin = pulX
        direction_pin = dirY if direction == 'right' else dirX
    elif axis == 'y':
        pul_pin = pulY
        direction_pin = dirY if direction == 'down' else dirX
    move_stepper(pul_pin, direction_pin, steps, delay)

def home_with_limit(axis, direction):
    """Home specified axis using limit switch"""
    print(f"Homing {axis}-axis toward {direction}...")
    if axis == 'x':
        pul_pin, dir_pin = pulX, dirY if direction == 'right' else dirX
        limit_switch = limit_switch_x
    else:
        pul_pin, dir_pin = pulY, dirY if direction == 'down' else dirX
        limit_switch = limit_switch_y
    
    dir_pin.on()
    while not limit_switch.is_pressed:
        pul_pin.on()
        time.sleep(0.001)
        pul_pin.off()
        time.sleep(0.001)
    dir_pin.off()
    print(f"{axis}-axis homed.")

def home_all():
    """Home both axes sequentially"""
    home_with_limit('x', 'left')
    home_with_limit('y', 'up')

def move_axes_simultaneously(x_dir, y_dir, x_steps, y_steps):
    """Threaded movement for both axes"""
    thread_x = threading.Thread(target=move_axis, args=('x', x_dir, x_steps))
    thread_y = threading.Thread(target=move_axis, args=('y', y_dir, y_steps))
    thread_x.start()
    thread_y.start()
    thread_x.join()
    thread_y.join()

# --- LiDAR Functions ---
def parse_stl19p_packet(packet):
    """Decode LiDAR data packet"""
    if len(packet) != 47 or packet[0] != 0x54 or packet[1] != 0x2C:
        return None
    
    start_angle = struct.unpack("<H", packet[4:6])[0] / 100.0
    end_angle = struct.unpack("<H", packet[42:44])[0] / 100.0
    
    points = []
    for i in range(12):
        offset = 6 + (i * 3)
        distance = struct.unpack("<H", packet[offset:offset+2])[0]
        angle = start_angle + (i * (end_angle - start_angle) / 11)
        points.append({"angle": angle, "distance": distance})
    
    return points

def monitor_elevators():
    """Continuous LiDAR monitoring"""
    lidar = serial.Serial(PORT, BAUDRATE, timeout=1)
    print("LiDAR elevator monitoring started...")
    
    try:
        while True:
            packet = lidar.read(47)
            if packet:
                points = parse_stl19p_packet(packet)
                if points:
                    for point in points:
                        if abs(point["angle"] - LEFT_ANGLE) < 5 and point["distance"] > BASELINE_LEFT + THRESHOLD:
                            press_elevator1_button_5()
                            break
                        elif abs(point["angle"] - RIGHT_ANGLE) < 5 and point["distance"] > BASELINE_RIGHT + THRESHOLD:
                            press_elevator2_button_5()
                            break
    except KeyboardInterrupt:
        lidar.close()

# --- Action Functions ---
def press_elevator1_button_5():
    """Full sequence for left elevator"""
    print("Moving to Left Elevator...")
    #home_all()
    move_axes_simultaneously('right', 'down', 600, 700)
    time.sleep(1)  # Simulate button press
    home_all()

def press_elevator2_button_5():
    """Full sequence for right elevator"""
    print("Moving to Right Elevator...")
    #home_all()
    move_axes_simultaneously('right', 'down', 800, 750)
    time.sleep(1)
    home_all()

# --- Testing Functions ---
def test_lidar():
    """Verify LiDAR detection"""
    print("\n=== LiDAR Self-Test ===")
    lidar = serial.Serial(PORT, BAUDRATE, timeout=1)
    
    try:
        print("Reading LiDAR for 5 seconds...")
        start_time = time.time()
        while time.time() - start_time < 5:
            packet = lidar.read(47)
            if packet:
                points = parse_stl19p_packet(packet)
                if points:
                    for p in points:
                        if abs(p["angle"] - LEFT_ANGLE) < 5:
                            print(f"Left: {p['angle']:.1f}° | {p['distance']}mm")
                        elif abs(p["angle"] - RIGHT_ANGLE) < 5:
                            print(f"Right: {p['angle']:.1f}° | {p['distance']}mm")
        print("LiDAR test complete. Verify angles/distances.")
    finally:
        lidar.close()

def test_steppers():
    """Validate motor movements"""
    print("\n=== Stepper Self-Test ===")
    
    print("Homing...")
    home_all()
    
    print("Testing X-axis...")
    move_axis('x', 'right', 200)
    time.sleep(1)
    home_with_limit('x', 'left')
    
    print("Testing Y-axis...")
    move_axis('y', 'down', 200)
    time.sleep(1)
    home_with_limit('y', 'up')
    
    print("Stepper test complete.")

def manual_test():
    """Interactive control mode"""
    print("\n=== Manual Test Mode ===")
    print("1: Test Left Elevator Position")
    print("2: Test Right Elevator Position")
    print("3: Emergency Home")
    print("q: Exit")
    
    while True:
        cmd = input("Select test: ").lower()
        if cmd == '1':
            press_elevator1_button_5()
        elif cmd == '2':
            press_elevator2_button_5()
        elif cmd == '3':
            home_all()
        elif cmd == 'q':
            break

# --- Main Program ---
if __name__ == "__main__":
    # Initialization
    print("=== Elevator Control System ===")
    print("Running startup tests...")
    test_steppers()
    test_lidar()
    
    # Start monitoring thread
    lidar_thread = threading.Thread(target=monitor_elevators, daemon=True)
    lidar_thread.start()
    
    # Main menu
    try:
        while True:
            print("\nMain Menu:")
            print("1: Manual Test Mode")
            print("2: Auto Monitoring Mode")
            print("q: Quit")
            choice = input("Select mode: ").lower()
            
            if choice == '1':
                manual_test()
            elif choice == '2':
                print("Auto monitoring active... (Ctrl+C to stop)")
                while True: time.sleep(1)
            elif choice == 'q':
                break
                
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")