#!/bin/bash
export GST_DEBUG="*:0"
# this ip is the docker machine ip docker0: see the value using
# ifconfig
# $1 = Topic in MQTT Server
# $2 = IP in MQTT Server
# $3 = PORT in MQTT Server

# inside container
python /root/voice_recognizer/voice_recognizer.py $1 $2 $3

# local
# python3 voice_recognizer.py $1 $2 $3