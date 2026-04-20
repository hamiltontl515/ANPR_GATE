import time
import RPi.GPIO as GPIO

class GateController:
    def __init__(self, in_pin=18, out_pin=23):
        GPIO.setmode(GPIO.BCM)

        self.in_pin = in_pin
        self.out_pin = out_pin

        GPIO.setup(in_pin, GPIO.OUT)
        GPIO.setup(out_pin, GPIO.OUT)

    def open_gate(self, gate_type):
        if gate_type == "IN":
            GPIO.output(self.in_pin, 1)
            time.sleep(2)
            GPIO.output(self.in_pin, 0)

        elif gate_type == "OUT":
            GPIO.output(self.out_pin, 1)
            time.sleep(2)
            GPIO.output(self.out_pin, 0)