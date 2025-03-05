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

# NEMA23 Stepper Motor (x-axis)
#ENAX = 17  #gpio
DIRX = 27  
PULX = 22  

# NEMA23 Stepper Motor (y-axis)
#ENAY = 23  #gpio
DIRY = 24  
PULY = 25 

dirX = LED(DIRX)
dirY = LED(DIRY)
pulX = LED(PULX)
pulY = LED(PULY)

#def move_stepper(ena, dir_pin, pul_pin, steps, delay=0.001):
def move_stepper(dir_pin, pul_pin, steps, delay=0.0015):

    dir_pin.on()
    
    for _ in range(steps):
        pul_pin.on()
        time.sleep(delay)
        pul_pin.off()
        time.sleep(delay)
    
    dir_pin.off()

move_stepper(dirX, pulX, 1000)      #dirX = left, dirY = right, pulX = horizontanl (x) movement,    1000 = # steps)
move_stepper(dirX, pulY, 500)       #dirX = up,   dirY = down,  pulY = vertical (y) movement,        500 = # steps)