# This Python file uses the following encoding: utf-8
'''
Capta o aúdio do microfone e envia em uma porta com o protocolo udp
Created by: Sidney Loyola de Sá
Date: 23/05/2020
Last Modified: 25/05/2020

Configuração:

IP = "172.17.0.1"
PORT = 8000

'''
import pyaudio
import socket
from threading import Thread

frames = []


def udpStream():
    # Metodo para transmitir o fluxo em uma porta udp
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), ("172.17.0.1", 8000))

    udp.close()


def record(stream, CHUNK):
    #captura o aúdio
    while True:
        frames.append(stream.read(CHUNK))


if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    # O parâmetro input=True captura o microfone
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    )

    Tr = Thread(target=record, args=(stream, CHUNK,))
    Ts = Thread(target=udpStream)
    Tr.setDaemon(True)
    Ts.setDaemon(True)
    Tr.start()
    Ts.start()
    Tr.join()
    Ts.join()
