# 2-26-25
#
# Auto Nav Cart Team - ECE 349 - University of Rochester
#
# First:
#   sudo apt-get update
#   sudo apt-get install python3-rpi.gpio
#
# ENA = enables / disables TB6600
# DIR = sets rotation of motor
# PUL = controls step pulses that make motor move
#
# TB6600(A) for Stepper Motor A (x-axis) 
# ENA(-) = GPIO17
# DIR(-) = GPIO27
# PUL(-) = GPIO22
#
# TB6600(B) for Stepper Motor B (y-axis) 
# ENA(-) = GPIO23
# DIR(-) = GPIO23
# PUL(-) = GPIO25

#import RPi.GPIO as GPIO
#import lgpio
from gpiozero import LED
import time

#GPIO.setmode(GPIO.BCM)

# connect ENA 1 and 2 to 5V power on Raspberry Pi?

# NEMA23 Stepper Motor (x-axis)
#ENAX = 17  #gpio
DIRX = 27  
PULX = 22  

# NEMA23 Stepper Motor (y-axis)
#ENAY = 23  #gpio
DIRY = 24  
PULY = 25 

# set all pins to output mode
#GPIO.setup(ENA1, GPIO.OUT)
#GPIO.setup(DIRX, GPIO.OUT)
#GPIO.setup(PULX, GPIO.OUT)
#GPIO.setup(ENA2, GPIO.OUT)
#GPIO.setup(DIRY, GPIO.OUT)
#GPIO.setup(PULY, GPIO.OUT)

#h = lgpio.gpiochip_open(0)

#lgpio.gpio_claim_output(h, DIRX)
#lgpio.gpio_claim_output(h, DIRY)
#lgpio.gpio_claim_output(h, PULX)
#lgpio.gpio_claim_output(h, PULY)
dirX = LED(DIRX)
dirY = LED(DIRY)
pulX = LED(PULX)
pulY = LED(PULY)

#def move_stepper(ena, dir_pin, pul_pin, steps, delay=0.001):
def move_stepper(dir_pin, pul_pin, steps, delay=0.002):

    #GPIO.output(ena, GPIO.HIGH)         # enable motor
    #GPIO.output(dir_pin, GPIO.HIGH)     # set direction
    #lgpio.gpio_write(h, dir_pin, 1)
    dirX.on()

    # generate pulses for the specified number of steps
    for _ in range(steps):
        #GPIO.output(pul_pin, GPIO.HIGH)
        #lgpio.gpio_write(h, pul_pin, 1)
        pulX.on()
        time.sleep(delay)
        #GPIO.output(pul_pin, GPIO.LOW)
        #lgpio.gpio_write(h, pul_pin, 0)
        pulX.off()
        time.sleep(delay)

    #GPIO.output(ena, GPIO.LOW)          # disable the motor after movement

move_stepper(DIRX, PULX, 1000)    # 1000 steps
move_stepper(DIRY, PULY, 500)     # 500 steps

#GPIO.cleanup()                          # clean up gpio configuration
#lgpio.gpio_free(h, DIRX)
#lgpio.gpio_free(h, DIRY)
#lgpio.gpio_free(h, PULX)
#lgpio.gpio_free(h, PULY)
#lgpio.gpiochip_close(h)
