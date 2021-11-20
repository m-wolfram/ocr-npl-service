#  OS
FROM ubuntu:18.04

#  Environment variables
ENV DOCKER_FLAG 1
ENV TESSDATA_PREFIX /tesseract-4.1.1/tessdata

#  Packages
RUN apt-get update \
  && apt-get install wget -y \
  && apt-get install ffmpeg libsm6 libxext6 -y \
  && apt install python3.7 -y \
  && apt install python3-pip -y \
  && pip3 install --upgrade pip

#  Tesseract compiling
RUN apt-get install libleptonica-dev -y \
	&& apt-get install automake -y \
	&& apt-get install unzip -y \
	&& apt-get install pkg-config -y \
	&& apt-get install libsdl-pango-dev -y \
	&& apt-get install libicu-dev -y \
	&& apt-get install libcairo2-dev -y \
	&& apt-get install bc -y
RUN wget https://github.com/tesseract-ocr/tesseract/archive/4.1.1.zip
RUN unzip 4.1.1.zip
RUN cd tesseract-4.1.1 \
  && ./autogen.sh \
  && ./configure \
  && make \
  && make install \
  && ldconfig
COPY ./traineddata /tesseract-4.1.1/tessdata

#  Python libraries
RUN python3 -m pip install opencv-python==4.5.4.58 \
  && python3 -m pip install pytesseract==0.3.7 \
  && python3 -m pip install natasha==1.4.0 \
  && python3 -m pip install Flask==2.0.2 \
  && python3 -m pip install requests==2.22.0 \
  && python3 -m pip install waitress==2.0.0 \
  && python3 -m pip install pandas==0.25.3