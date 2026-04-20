import json
import time
import paho.mqtt.client as mqtt

class ThingsBoardClient:
    def __init__(self, host, token):
        self.client = mqtt.Client()
        self.client.username_pw_set(token)
        self.client.connect(host, 1883, 60)

    def send_event(self, plate, zone):
        payload = {
            "plate": plate,
            "zone": zone,
            "timestamp": int(time.time())
        }

        self.client.publish(
            "v1/devices/me/telemetry",
            json.dumps(payload)
        )