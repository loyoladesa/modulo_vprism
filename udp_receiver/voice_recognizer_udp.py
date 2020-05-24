# This Python file uses the following encoding: utf-8
'''
Módulo para reconhecimento de voz recebido em uma porta com o protocolo udp.
Desenvolvido por Sidney Loyola de Sá
Data: 23/05/2020
'''

import pyaudio
import socket
import speech_recognition as sr
from threading import Thread

frames = []


def udpStream(CHUNK):
    # Método para receber o fluxo udp
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # define o IP e a porta
    udp.bind(("localhost", 12345))

    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)

    udp.close()


def play(stream, CHUNK):
    # método para manipular o aúdio recebido
    BUFFER = 10
    while True:
        if len(frames) == BUFFER:
            while True:
                print("Recebendo Aúdio")


                microfone = sr.Recognizer()

                # A próxima linha capta a fonte do aúdio
                with sr.Microphone() as source:

                    # Chama um algoritmo de reducao de ruidos no som
                    microfone.adjust_for_ambient_noise(source)

                    # Armazena o aúdio em uma variável
                    audio = microfone.listen(source)
                    stream.write(frames.pop(0), CHUNK)


                try:

                    # Passa a variável para o algoritmo reconhecedor de padroes
                    frase = microfone.recognize_google(audio, language='pt-BR')
                    # Retorna a frase pronunciada
                    print("Você disse: " + frase)



                # Se nao reconheceu o padrao de fala, exibe a mensagem
                except:
                    print("*******")

                print(frase)



if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    print("aqui!!!")

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK,
                    )

    Ts = Thread(target=udpStream, args=(CHUNK,))
    Tp = Thread(target=play, args=(stream, CHUNK,))

    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Ts.start()
    Tp.start()
    Ts.join()
    Tp.join()
