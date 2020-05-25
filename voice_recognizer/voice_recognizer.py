# This Python file uses the following encoding: utf-8
'''
Reconhecimento de voz de fluxo recebido em uma porta com o protocolo UDP.
Envia o Texto para um servidor mqtt
Created by: Sidney Loyola de Sá
Date: 23/05/2020
Last Modified: 25/05/2020

Parâmetros:

[1] : Tópico MQTT
[2] : Hostname MQTT
[3] : PORTA MQTT

Servidor MQTT para teste:
TÓPICO: v-prism
Hostname: env-3019652.users.scale.virtualcloud.com.br
Porta: 11002

Configuração:

IP = "172.17.0.1"
PORT = 8000

'''

import socket
import sys
import time
from threading import Thread

import paho.mqtt.client as mqtt
import pyaudio
import speech_recognition as sr


frames = []

#variável para armazenar o texto gerado pelo aúdio
frase = "vazia"

#variável booleana de controle
recebeu = False

#cria a instância de cliente mqtt
client = mqtt.Client("vms_voice_recognizer")



def udpStream(CHUNK, IP, PORT):
    # Função para receber o fluxo udp

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # define o IP e a porta
    udp.bind((IP, PORT))

    while True:
        sound_data, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(sound_data)

    udp.close()


def play(stream, CHUNK):
    # Função para manipular o aúdio recebido

    buffer = 10
    global frase
    global recebeu

    while True:
        if len(frames) == buffer:
            while True:
                print("Recebendo Fluxo de Aúdio:")

                voice_recognizer = sr.Recognizer()

                # A próxima linha capta a fonte do aúdio
                with sr.Microphone() as source:

                    # Chama um algoritmo de reducao de ruidos no som
                    voice_recognizer.adjust_for_ambient_noise(source)

                    # Armazena o aúdio em uma variável
                    audio = voice_recognizer.listen(source)
                    stream.write(frames.pop(0), CHUNK)

                try:

                    # Passa a variável para o algoritmo reconhecedor de padroes
                    # Transforma o Texto em Audio
                    frase = voice_recognizer.recognize_google(audio, language='pt-BR')
                    recebeu = True




                # Se nao reconheceu o padrao de fala, exibe a mensagem
                # Deixei para decidir posteriormente qual mensagem exibir
                except:
                    print("")



def on_message(client, userdata, message):
    #Função Callback do client mqtt para ver a mensagem que foi enviada
    print("message send ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)


def send(mqtt_topic):
    #Função para enviar o texto para um servidor mqtt

    while True:
        global recebeu
        global client


        if recebeu:
            #se recebeu aúdio e ele foi transformado em texto
            client.loop_start()
            client.subscribe(mqtt_topic) # se inscreve no tópico
            client.publish(mqtt_topic, frase) # envia para o servidor
            time.sleep(4)
            client.loop_stop()
            recebeu = False




if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100
    IP = "172.17.0.1"
    PORT = 8000

    mqtt_topic = sys.argv[1]
    mqtt_hostname = sys.argv[2]
    mqtt_port = int(sys.argv[3])

    client.on_message = on_message
    client.connect(mqtt_hostname, mqtt_port)

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK,
                    )



    Ts = Thread(target=udpStream, args=(CHUNK, IP, PORT,))
    Tp = Thread(target=play, args=(stream, CHUNK,))
    Te = Thread(target=send, args=(mqtt_topic,))

    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Te.setDaemon(True)
    Ts.start()
    Tp.start()
    Te.start()
    Ts.join()
    Tp.join()
    Te.join()
