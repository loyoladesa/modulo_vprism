import pyaudio
import socket
import speech_recognition as sr
from threading import Thread

frames = []


def udpStream(CHUNK):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("localhost", 12345))

    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 2)
        frames.append(soundData)



    udp.close()


def play(stream, CHUNK):
    BUFFER = 10
    while True:
        if len(frames) == BUFFER:
            while True:
                stream.write(frames.pop(0), CHUNK)
                microfone = sr.Recognizer()

                with sr.Microphone(pyaudio.PyAudio().get_device_count() - 1) as source:

                    # Chama um algoritmo de reducao de ruidos no som
                    microfone.adjust_for_ambient_noise(source)

                    audio = microfone.listen(source)

                try:

                    # Passa a variável para o algoritmo reconhecedor de padroes
                    frase = microfone.recognize_google(audio, language='pt-BR')

                    # Retorna a frase pronunciada
                    print("Você disse: " + frase)

                # Se nao reconheceu o padrao de fala, exibe a mensagem
                except sr.UnkownValueError:
                    print("Não entendi")




if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

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
