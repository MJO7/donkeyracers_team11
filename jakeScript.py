import argparse
import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import numpy as np

parser = argparse.ArgumentParser(description="Motor testing script!")
parser.add_argument('-e', '--esc', type=int, default=1, help='ESC channel (default: 1)')
parser.add_argument('-s', '--servo', type=int, default=0, help='Servo channel (default: 0)')
parser.add_argument('-i', '--initialize', type=int, default=0, help='Is the motor running for the first time since being switched on? (default: 0)')
args = parser.parse_args()
ESC_CHANNEL = args.esc
SERVO_CHANNEL = args.servo
INITIALIZE = args.initialize

# === Constants ===
FREQ = 60

ESC_NEUTRAL = 1500
ESC_MAX = 1850
ESC_MIN = 1050

SERVO_NEUTRAL = 1650
SERVO_LEFT = 1900
SERVO_RIGHT = 1000

# Setup I2C bus and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = FREQ

def calcDutyCycle(microseconds):
    calcVal = int(microseconds / 1000 / (1 / 60 * 1000) * 65535)
    print(calcVal)
    return calcVal

if INITIALIZE == 1:
    print(f"Arming ESC on channel {ESC_CHANNEL}...")
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    time.sleep(2.0)
    print("ESC is armed.")
else:
    print("Skipping initialization. Ensure ESC was already armed!")

def setBackwards():
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    time.sleep(0.5)
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(1300)
    time.sleep(0.5)
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    time.sleep(0.5)

def setForward():
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    time.sleep(0.5)
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(1600)
    time.sleep(0.5)
    pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    time.sleep(0.5)

def setMotorSpeed(length):
    if length > ESC_MAX or length < ESC_MIN:
        print(f"Error: ESC value {length} out of range ({ESC_MIN}-{ESC_MAX}). Setting to neutral.")
        pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(ESC_NEUTRAL)
    else:
        if length < 1562 and length > 1399 and length != ESC_NEUTRAL:
            print("input may be too weak")
        pca.channels[ESC_CHANNEL].duty_cycle = calcDutyCycle(length)
    time.sleep(1.0)

def setServoAngle(length):
    if length > SERVO_LEFT or length < SERVO_RIGHT:
        print(f"Error: Servo value {length} out of range ({SERVO_RIGHT}-{SERVO_LEFT}). Setting to neutral.")
        pca.channels[SERVO_CHANNEL].duty_cycle = calcDutyCycle(SERVO_NEUTRAL)
    else:
        pca.channels[SERVO_CHANNEL].duty_cycle = calcDutyCycle(length)
    time.sleep(1.0)

# go forward at quarter speed
print("moving forward at quarter speed")
setMotorSpeed(int(ESC_NEUTRAL + (ESC_MAX - ESC_NEUTRAL) / 4))
time.sleep(2.0)

# pause
print("pausing")
setMotorSpeed(ESC_NEUTRAL)
time.sleep(2.0)

# go backward at quarter speed
print("setting backwards mode")
setBackwards()
print("moving backward at quarter speed")
setMotorSpeed(int(ESC_NEUTRAL - (ESC_NEUTRAL - ESC_MIN) / 4))
time.sleep(3.0)

# back to forward mode and go forward at quarter speed again
print("returning to forward and moving at quarter speed")
setMotorSpeed(ESC_NEUTRAL)
time.sleep(0.5)
setMotorSpeed(int(ESC_NEUTRAL + (ESC_MAX - ESC_NEUTRAL) / 4))
time.sleep(2.0)

# stop
print("stopping")
setMotorSpeed(ESC_NEUTRAL)

# steer fully left
print("steering fully left")
setServoAngle(SERVO_LEFT)

# steer fully right
print("steering fully right")
setServoAngle(SERVO_RIGHT)

# return to neutral
print("returning to neutral")
setServoAngle(SERVO_NEUTRAL)

pca.deinit()
