
'''
Reconhecimento de voz de fluxo recebido em uma porta com o protocolo UDP.
Envia o Texto para um servidor mqtt
Created by: Sidney Loyola de Sá
Date: 23/05/2020
Last Modified: 10/07/2020

Parâmetros:

[1] : Tópico MQTT
[2] : Hostname MQTT
[3] : PORTA MQTT
[4]: MODE - ON - utiliza API do google (precisa de Internet) OFF - utiliza o Sphinx - Executa Offline

Configuração:

IP = "localhost"
PORT = 5000

'''


import sys
import time
import paho.mqtt.publish as publish
import pyaudio
import socket
import speech_recognition as sr
from threading import Thread
import io
import wave
from os import path
import tempfile

from speech_recognition import AudioFile

frames = []
logs = []
mode = ""

#variável booleana de controle
transcreveuAudio = False
API_funcionou = True


def udpStream(CHUNK, IP, PORT):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # define o IP e a porta
    udp.bind(('', PORT))



    while True:
        sound_data, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(sound_data)


    udp.close()


def transcribe(CHUNK):
    # Função para manipular o aúdio recebido

    buffer = 10
    print("Recebendo Fluxo de Aúdio:",flush=True)

    global frase
    global transcreveuAudio


    while True:

        if len(frames) == buffer:
            #print("buffer carregado")

            while True:

                    # Acessa a biblioteca SpeechRecognition
                    voice_recognizer = sr.Recognizer()

                    # Grava arquivo temporario para facilitar a transcrição
                    arquivoTemporario = tempfile.TemporaryFile()
                    #arquivoTemporario = 'output.wav'

                    with wave.open(arquivoTemporario, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                    arquivoTemporario.seek(0)

                    #print("Arquivo Criado")

                    # A próxima linha capta a fonte do aúdio
                    with sr.AudioFile(arquivoTemporario) as source:

                        # Chama um algoritmo de reducao de ruidos no som
                        #voice_recognizer.adjust_for_ambient_noise(source)

                        #print("Armazena o aúdio em uma variável")
                        audio = voice_recognizer.record(source)

                    if (mode == "OFF"):
                        try:
                            # Acessa a API
                            frase = voice_recognizer.recognize_sphinx(audio)
                            print("Audio: " + frase, flush=True)
                            transcreveuAudio = True
                            temAudio = False
                            frames.clear()

                        # Se nao reconheceu o padrao de fala registra no log
                        except sr.UnknownValueError:
                            msg = "Sphinx could not understand audio"
                            '''cont = cont + 1
                            if(cont==10):
                                print(msg,flush=True)
                                cont = 0'''

                    else:
                        try:
                            #print("Acessa a API Google")
                            frase = voice_recognizer.recognize_google(audio)
                            print("Audio: " + frase, flush=True)
                            transcreveuAudio = True
                            temAudio = False
                            frames.clear()

                        # Se nao reconheceu o padrao de fala registra no log
                        except sr.UnknownValueError:
                            msg=''
                            #print("Google could not understand audio")


                    arquivoTemporario.close()


def send(mqtt_topic):
    #Função para enviar o texto para um servidor mqtt

    while True:
        global transcreveuAudio

        if transcreveuAudio:
            #Publica no servidor MQTT se recebeu aúdio e ele foi transformado em texto
            #publish.single(topic=mqtt_topic,payload=frase, hostname=mqtt_hostname, port=int(mqtt_port))
            transcreveuAudio = False




if __name__ == "__main__":
    print("VMS Speech To Text: Inicializado", flush=True)
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100
    IP = "localhost"
    PORT = 5000

    mqtt_topic = sys.argv[1]
    mqtt_hostname = sys.argv[2]
    mqtt_port = int(sys.argv[3])
    mode = sys.argv[4]

    #Utilizado para debugar o desenvolvimento do VMS
    #print("TOPIC: "+mqtt_topic,flush=True)
    #print("HOSTNAME: "+mqtt_hostname,flush=True)
    #print("PORT: "+str(mqtt_port),flush=True)
    #print("MODE: "+mode,flush=True)


    Ts = Thread(target=udpStream, args=(CHUNK, IP, PORT,))
    Tp = Thread(target=transcribe, args=(CHUNK,))
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