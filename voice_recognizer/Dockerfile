# This is a sample Dockerfile you can modify to deploy your own app based on voice_recognizer

FROM python:3.6-slim-stretch



RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    libasound2-dev \
    libasound-dev \
    libpulse-dev \
    portaudio19-dev \
    libportaudio2  \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    swig \
    zip \
    bash \
    python-gi \
    python-gi-cairo \
    python-dbus \
    gir1.2-gtk-3.0 \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-plugins-bad \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


# The rest of this file just runs an example script.

# If you wanted to use this Dockerfile to run your own app instead, maybe you would do this:
# COPY . /root/your_app_or_whatever
# RUN cd /root/your_app_or_whatever && \
#     pip3 install -r requirements.txt
# RUN whatever_command_you_run_to_start_your_app

RUN apt-get install -y --fix-missing \
    python3-gi \
    python3-gst-1.0

#RUN apt-get install libasound-dev
#RUN apt-get update
#RUN apt-get install libasound2-dev


#RUN apt-get --assume-yes install libasound-dev portaudio19-dev     libportaudio2 libportaudiocpp0
RUN pip3 install pyaudio
RUN pip3 install websocket-client
RUN pip3 install playsound

#RUN apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0


#RUN apt-get install python3 python3-all-dev python3-pip build-essential swig git libpulse-dev

#RUN apt-get install portaudio19-dev python-pyaudio
#RUN apt-get install python3 python3-all-dev python3-pip build-essential swig git libpulse-dev libasound2-dev

RUN python -m pip install --upgrade pip

#RUN apt-get install python-pyaudio python3-pyaudio

RUN pip3 install paho-mqtt
RUN pip3 install opencv-python
RUN pip3 install numpy==1.15.4

RUN pip3 install pocketsphinx

RUN pip3 install SpeechRecognition
#RUN pip3 install PyAudio

RUN apt-get install -y --fix-missing libgirepository1.0-dev
RUN pip install --no-binary gobject PyGObject
RUN apt-get install -y --fix-missing gstreamer1.0-libav
RUN apt-get install -y --fix-missing \
    tcpdump \
    net-tools

COPY . /root/voice_recognizer

ENTRYPOINT ["./root/voice_recognizer/start.sh"]