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
lib = ""

homeDir = path.abspath(path.dirname(__file__))  # obtemos o diretório home
logFile = path.join(homeDir, "audio_recognizer.log")  # criamos o nome do arquivo de logger

# Criamos o logger
logger = logging.getLogger(__name__)  # __name__ é uma variável que contem o nome do módulo. Assim, saberemos que módulo emitiu a mensagem
logger.setLevel(logging.INFO)  # neste experimento queremos apresentar apenas as mensagens de INFO e as inferiores (WARNING, ERROR, CRITICAL)


# Criamos um handler para enviar as mensagens para um arquivo
logger_handler = logging.FileHandler(logFile, mode='w')
logger_handler.setLevel(logging.INFO)

# o mode="w" faz com que a cada nova execução do programa, o logger anterior é apagado.
#Use a forma mode="a" para adicionar novas mensagens sem apagar o arquivo anterior

# Especifique a formatação da mensagem
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Associe esta formatação ao  Handler
logger_handler.setFormatter(logger_formatter)

# Associe o Handler ao  Logger
logger.addHandler(logger_handler)

# Para emitir uma mensagem no nível info utilizamos a forma:
logger.info('Logger OK')

#outras formas possíveis:
# .logger.critical(msg)
#.logger.error(msg)
#.logger.warning(msg)

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
    print("Recebendo Fluxo de Aúdio:",flush=True)
    #print(p.get_sample_size(FORMAT))

    global frase
    global recebeu

    while True:
        if len(frames) == buffer:
            while True:

                voice_recognizer = sr.Recognizer()
                arquivoTemporario = tempfile.TemporaryFile()



                with wave.open(arquivoTemporario, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))

                arquivoTemporario.seek(0)


                # A próxima linha capta a fonte do aúdio
                with sr.AudioFile(arquivoTemporario) as source:

                    # Chama um algoritmo de reducao de ruidos no som
                    voice_recognizer.adjust_for_ambient_noise(source)

                    # Armazena o aúdio em uma variável
                    audio = voice_recognizer.record(source)

                if(lib == "OFF"):
                    try:
                        # Passa a variável para o algoritmo reconhecedor de padroes
                        # Transforma o Audio em Texto
                        frase = voice_recognizer.recognize_sphinx(audio)
                        print("Audio: " + frase,flush=True)
                        recebeu = True
                        frames.clear()

                    # Se nao reconheceu o padrao de fala registra no log
                    except sr.UnknownValueError:
                        msg = "Sphinx could not understand audio"
                        logger.error(msg)
                    except sr.RequestError as e:
                        msg = "Sphinx error; {0}".format(e)
                        logger.error(msg)
                else:
                    try:

                        # Passa a variável para o algoritmo reconhecedor de padroes
                        # Transforma o Audio em Texto
                        frase = voice_recognizer.recognize_google(audio)
                        print("Audio: " + frase,flush=True)
                        recebeu = True
                        frames.clear()

                    # Se nao reconheceu o padrao de fala registra no log
                    except sr.UnknownValueError:
                        msg = "Google could not understand audio"
                        logger.error(msg)
                    except sr.RequestError as e:
                        msg = "Google error; {0}".format(e)
                        logger.error(msg)



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
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100
    IP = "localhost"
    PORT = 12345

    mqtt_topic = sys.argv[1]
    mqtt_hostname = sys.argv[2]
    mqtt_port = int(sys.argv[3])
    lib = sys.argv[4]

    print(mqtt_topic,flush=True)
    print(mqtt_hostname,flush=True)
    print(mqtt_port,flush=True)
    print(lib,flush=True)

    client.on_message = on_message
    #client.connect(mqtt_hostname, mqtt_port)

    #p = pyaudio.PyAudio()

    stream = ""
    '''stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=true,
                    frames_per_buffer=CHUNK,
                    )'''



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
