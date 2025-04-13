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
LEFT_ANGLE = 45.0    # Adjust based on physical setup
RIGHT_ANGLE = 315.0
THRESHOLD = 500      # mm change to detect door open
BASELINE_LEFT = 1000 # Measure with doors closed
BASELINE_RIGHT = 1000

# --- Stepper Control Functions ---
def move_stepper(pul_pin, direction_pin, steps, delay=0.0015):
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

def scan_lidar(duration=5):
    """Efficient LiDAR scanning with summarized output"""
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as lidar:
            print(f"\nScanning LiDAR for {duration}s (Ctrl+C to stop)...")
            
            # Data containers
            left_data = []
            right_data = []
            last_print = 0
            
            start_time = time.time()
            while time.time() - start_time < duration:
                packet = lidar.read(47)
                if packet and packet[0] == 0x54 and packet[1] == 0x2C:
                    points = parse_stl19p_packet(packet)
                    if points:
                        now = time.time()
                        for p in points:
                            if abs(p["angle"] - LEFT_ANGLE) < 5:
                                left_data.append(p["distance"])
                            elif abs(p["angle"] - RIGHT_ANGLE) < 5:
                                right_data.append(p["distance"])
                        
                        # Throttle output to 1Hz
                        if now - last_print >= 1.0:
                            print("\n=== Summary ===")
                            if left_data:
                                print(f"Left Elevator: Min={min(left_data)}mm | Avg={sum(left_data)/len(left_data):.1f}mm | Max={max(left_data)}mm")
                            if right_data:
                                print(f"Right Elevator: Min={min(right_data)}mm | Avg={sum(right_data)/len(right_data):.1f}mm | Max={max(right_data)}mm")
                            last_print = now
                
                elif packet:
                    print(f"! Invalid packet header: {packet[:2].hex()}")
            
            # Final summary
            print("\n=== Final Scan Results ===")
            print(f"Left samples: {len(left_data)} | Right samples: {len(right_data)}")
    
    except serial.SerialException as e:
        print(f"! LiDAR error: {e}")

# --- Action Functions ---
def press_elevator1_button_5():
    """Full sequence for left elevator"""
    print("Moving to Left Elevator...")
    move_axes_simultaneously('right', 'down', 600, 700)
    time.sleep(1)  # Simulate button press

def press_elevator2_button_5():
    """Full sequence for right elevator"""
    print("Moving to Right Elevator...")
    move_axes_simultaneously('right', 'down', 800, 750)
    time.sleep(1)

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

# --- Main Program ---
if __name__ == "__main__":
    print("=== Elevator Control System ===")
    
    try:
        while True:
            print("\n=== MAIN MENU ===")
            print("1: Home All Axes")
            print("2: Move to Left Elevator")
            print("3: Move to Right Elevator")
            print("4: Scan LiDAR (5 sec)")
            print("5: Test Steppers")
            print("q: Quit")
            
            choice = input("Select option: ").strip().lower()
            
            if choice == '1':
                home_all()
            elif choice == '2':
                press_elevator1_button_5()
            elif choice == '3':
                press_elevator2_button_5()
            elif choice == '4':
                scan_lidar()
            elif choice == '5':
                test_steppers()
            elif choice == 'q':
                break
            else:
                print("Invalid option!")
                
    except KeyboardInterrupt:
        pass
        
    print("\nSystem shutdown complete.")