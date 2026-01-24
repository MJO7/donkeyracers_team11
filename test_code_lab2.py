#!/usr/bin/env python3
# Simple ESC + Servo PWM stress test for Raspberry Pi using pigpio
# Install once:
#   sudo apt update
#   sudo apt install -y pigpio python3-pigpio
#   sudo systemctl enable --now pigpiod
#
# Run:
#   python3 simple_pwm_stress.py
#
# SAFETY: run with wheels off the ground first.

import time
import random
import pigpio

ESC_GPIO   = 18   # BCM pin for ESC signal
SERVO_GPIO = 19   # BCM pin for servo signal

ESC_MIN, ESC_MAX, ESC_NEUTRAL = 1000, 2000, 1500
SERVO_MIN, SERVO_MAX, SERVO_CENTER = 1000, 2000, 1500

DWELL = 0.25      # seconds to hold each command
TOTAL = 60        # total test time (seconds)

def set_pw(pi, esc_us, servo_us):
    pi.set_servo_pulsewidth(ESC_GPIO,   esc_us)
    pi.set_servo_pulsewidth(SERVO_GPIO, servo_us)

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpio not running. Start with: sudo systemctl start pigpiod")

try:
    # Arm / safe start
    set_pw(pi, ESC_NEUTRAL, SERVO_CENTER)
    time.sleep(3)

    start = time.time()

    # 1) Grid test (covers many combinations)
    esc_vals   = [1000, 1200, 1500, 1800, 2000]
    servo_vals = [1000, 1250, 1500, 1750, 2000]
    for e in esc_vals:
        for s in servo_vals:
            set_pw(pi, e, s)
            time.sleep(DWELL)

    # 2) Random stress until TOTAL seconds
    while time.time() - start < TOTAL:
        e = random.choice([ESC_MIN, ESC_NEUTRAL, ESC_MAX, random.randint(ESC_MIN, ESC_MAX)])
        s = random.choice([SERVO_MIN, SERVO_CENTER, SERVO_MAX, random.randint(SERVO_MIN, SERVO_MAX)])
        set_pw(pi, e, s)
        time.sleep(DWELL)

finally:
    # Failsafe: stop motor + center steering
    set_pw(pi, ESC_NEUTRAL, SERVO_CENTER)
    time.sleep(1)
    pi.stop()
