import time
import paho.mqtt.client as mqtt
from grovepi import *


ENTRY_SERVO = 5
EXIT_SERVO = 6

pinMode(ENTRY_SERVO, "OUTPUT")
pinMode(EXIT_SERVO, "OUTPUT")

OPEN_DURATION = 5

barriers = {"entry":{"port": ENTRY_SERVO, "state":"CLOSED", "opened_at": 0},
            "exit":{"port":EXIT_SERVO, "state": "CLOSED","opened_at":0}
            }

def open_barrier(name):
    b = barriers[name]
    if b["state"] != "OPEN":
        servoWrite(b["port"], 90)
        b["state"] = "OPEN"
        b["opened_at"] = time.time()
        print(f"{name} opened")

def close_barrier(name):
    b = barriers[name]
    servoWrite(b["port"], 0)
    b["state"] = "CLOSED"
    print(f"{name} clsed")

def on_connect(client,userdata,flags, rc):
    print("Connected")
    client.subscribe("Barrier/entry/control")
    client.subscribe("Barrier/exit/control")
    
def on_message(client,userdata,msg):
    topic = msg.topic
    command = msg.payload.decode()
    
    if topic == "barrier/entry/control" and command == "OPEN":
        open_barrier("entry")
        
    elif topic == "barrier/exit/control" and command == "OPEN":
        open_barrier("exit")
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost",1883,60)

client.loop_start()

while True:
    now = time.time()
    
    for name, b in barriers.items():
        if b["state"] == "OPEN" and (now - b["opened_at"] > OPEN_DURATION):
            close_barrier(name)
    
    time.sleep(0.1)

        