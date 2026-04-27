import grovepi
import time

servo_port = 5

grovepi.pinMode(servo_port,"OUTPUT")

print("moving ro 90")
grovepi.servoWrite(servo_port,90)
time.sleep(2)

print("moving to 0")
grovepi.servoWrite(servo_port, 0)
