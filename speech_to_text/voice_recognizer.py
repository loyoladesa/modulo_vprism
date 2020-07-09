'''
Reconhecimento de voz de fluxo recebido em uma porta com o protocolo UDP.
Envia o Texto para um servidor mqtt
Created by: Sidney Loyola de Sá
Date: 23/05/2020
Last Modified: 07/07/2020

Parâmetros:

[1] : Tópico MQTT
[2] : Hostname MQTT
[3] : PORTA MQTT
[4]: MODE - ON - utiliza API do google (precisa de Internet) OFF - utiliza o Sphinx - Executa Offline

Servidor MQTT para teste:
TÓPICO: v-prism
Hostname: env-3019652.users.scale.virtualcloud.com.br
Porta: 11002

Configuração:

IP = "localhost"
PORT = 12345

'''


import sys
import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt


import pyaudio
import socket
import speech_recognition as sr
from threading import Thread
import io
import wave
from os import path
import tempfile
import logging


frames = []
logs = []
mode = ""

#variável booleana de controle
recebeu = False

#cria a instância de cliente mqtt
client = mqtt.Client("vms_voice_recognizer")



def udpStream(CHUNK, IP, PORT):
    print("Função para receber o fluxo udp", flush=True)


    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # define o IP e a porta
    udp.bind(('', PORT))

    while True:
        #print("recebendo ...",flush=True)
        sound_data, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(sound_data)

    udp.close()


def transcribe(CHUNK):
    # Função para manipular o aúdio recebido

    buffer = 10
    print("Recebendo Fluxo de Aúdio:",flush=True)

    global frase
    global recebeu

    while True:
        if len(frames) == buffer:
            while True:
                #print("Análise do Buffer")
                voice_recognizer = sr.Recognizer()
                arquivoTemporario = tempfile.TemporaryFile()

                with wave.open(arquivoTemporario, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                arquivoTemporario.seek(0)

                #print("Terminou de Montar o Arquivo Temporário")


                # A próxima linha capta a fonte do aúdio
                with sr.AudioFile(arquivoTemporario) as source:

                    # Chama um algoritmo de reducao de ruidos no som
                    voice_recognizer.adjust_for_ambient_noise(source)

                    #print("Armazena o aúdio em uma variável")
                    audio = voice_recognizer.record(source)

                if(mode == "OFF"):
                    try:
                        # Passa a variável para o algoritmo reconhecedor de padroes
                        #print("Transforma o Audio em Texto Sphinx",flush=True)
                        frase = voice_recognizer.recognize_sphinx(audio)
                        print("Audio: " + frase, flush=True)
                        recebeu = True
                        frames.clear()

                    # Se nao reconheceu o padrao de fala registra no log
                    except sr.UnknownValueError:
                        msg = "Sphinx could not understand audio"
                       # print(msg,flush=True)
                    except sr.RequestError as e:
                        msg = "Sphinx error; {0}".format(e)
                        #print(msg,flush=True)
                else:
                    try:
                        # Passa a variável para o algoritmo reconhecedor de padroes
                        #print("Transforma o Audio em Texto Google",flush=True)
                        frase = voice_recognizer.recognize_google(audio)
                        print("Audio: " + frase,flush=True)
                        recebeu = True
                        frames.clear()

                    # Se nao reconheceu o padrao de fala registra no log
                    except sr.UnknownValueError:
                        msg = "Google could not understand audio"
                       # print(msg,flush=True)
                    except sr.RequestError as e:
                        msg = "Google error; {0}".format(e)
                       # print(msg,flush=True)

                arquivoTemporario.close()


def on_message(client, userdata, message):
    #Função Callback do client mqtt para ver a mensagem que foi enviada
    print("message send ", str(message.payload.decode("utf-8")),flush=True)
    print("message topic=", message.topic,flush=True)


def send(mqtt_topic):
    #Função para enviar o texto para um servidor mqtt

    while True:
        global recebeu
        global client


        if recebeu:
            #se recebeu aúdio e ele foi transformado em texto
            '''client.loop_start()
            client.subscribe(mqtt_topic) # se inscreve no tópico
            client.publish(mqtt_topic, frase) # envia para o servidor
            time.sleep(4)
            client.loop_stop()'''

            publish.single(mqtt_topic,frase, hostname=mqtt_hostname, port=int(mqtt_port))
            recebeu = False




if __name__ == "__main__":
    print("Voice Recognizer", flush=True)
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100
    IP = "localhost"
    PORT = 5000

    print("porta: "+str(PORT))

    mqtt_topic = sys.argv[1]
    mqtt_hostname = sys.argv[2]
    mqtt_port = int(sys.argv[3])
    mode = sys.argv[4]

    print("TOPIC: "+mqtt_topic,flush=True)
    print("HOSTNAME: "+mqtt_hostname,flush=True)
    print("PORT: "+str(mqtt_port),flush=True)
    print("MODE: "+mode,flush=True)

    client.on_message = on_message
    #client.connect(mqtt_hostname, mqtt_port)

    Ts = Thread(target=udpStream, args=(CHUNK, IP, PORT,))
    Tp = Thread(target=transcribe, args=(CHUNK,))
    Te = Thread(target=send, args=(mqtt_topic,))

    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Te.setDaemon(True)

    print("Start udp", flush=True)
    Ts.start()

    Tp.start()
    Te.start()
    Ts.join()
    Tp.join()
    Te.join()