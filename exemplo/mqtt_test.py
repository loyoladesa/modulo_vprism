# This Python file uses the following encoding: utf-8

import paho.mqtt.client as mqtt
import time


def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)


client = mqtt.Client("vms_voice_recognizer")
client.on_message = on_message
client.connect("env-3019652.users.scale.virtualcloud.com.br", 11002)
client.loop_start()
client.subscribe("v-prism")
client.publish("v-prism", "reconhecimento de voz")
time.sleep(4)
client.loop_stop()
