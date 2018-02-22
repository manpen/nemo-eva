FROM python:3.6-stretch as nemo-eva

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

RUN mkdir /data
COPY data/paper-features.csv /data/paper-features.csv
COPY src /src

WORKDIR /src
CMD main.py

FROM nemo-eva as nemo-eva-dev

RUN pip3 install pycodestyle pytest pytest-ordering
