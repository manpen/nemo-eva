FROM python:3.6-stretch

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

COPY src /src

WORKDIR /src
CMD main.py
