#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

# ====== EDIT THESE ======
ESC_PIN_BCM   = 18   # ESC signal pin (BCM numbering)
SERVO_PIN_BCM = 13   # Servo signal pin (BCM numbering)

FREQ_HZ = 50         # 50 Hz standard for servo/ESC PWM
PERIOD_US = 1_000_000 / FREQ_HZ  # 20,000 us at 50 Hz

ESC_NEUTRAL_US  = 1500  # many reversible ESCs; if forward-only, try 1000 as "stop"
SERVO_CENTER_US = 1500

esc_values_us   = [ESC_NEUTRAL_US, 1600, 1700, ESC_NEUTRAL_US]
servo_values_us = [1300, SERVO_CENTER_US, 1700, SERVO_CENTER_US]

HOLD_SEC = 1.0
# =======================

def us_to_duty(us: int) -> float:
    # duty cycle (%) = pulse_width / period * 100
    return (us / PERIOD_US) * 100.0

def set_pulse_us(pwm_obj, us: int):
    pwm_obj.ChangeDutyCycle(us_to_duty(us))

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ESC_PIN_BCM, GPIO.OUT)
    GPIO.setup(SERVO_PIN_BCM, GPIO.OUT)

    esc_pwm = GPIO.PWM(ESC_PIN_BCM, FREQ_HZ)
    servo_pwm = GPIO.PWM(SERVO_PIN_BCM, FREQ_HZ)

    # Start PWM at neutral/center (arming-safe)
    esc_pwm.start(us_to_duty(ESC_NEUTRAL_US))
    servo_pwm.start(us_to_duty(SERVO_CENTER_US))
    print(f"Arming: ESC={ESC_NEUTRAL_US}us SERVO={SERVO_CENTER_US}us")
    time.sleep(2.0)

    try:
        while True:
            for e in esc_values_us:
                for s in servo_values_us:
                    set_pulse_us(esc_pwm, e)
                    set_pulse_us(servo_pwm, s)
                    print(f"ESC={e}us  SERVO={s}us")
                    time.sleep(HOLD_SEC)

    except KeyboardInterrupt:
        print("\nStopping: neutral/center...")

    finally:
        # Safety stop
        set_pulse_us(esc_pwm, ESC_NEUTRAL_US)
        set_pulse_us(servo_pwm, SERVO_CENTER_US)
        time.sleep(1.0)

        esc_pwm.stop()
        servo_pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()

