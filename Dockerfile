FROM python:3.6-alpine3.7 as nemo-eva

COPY requirements.txt /requirements.txt

RUN apk --no-cache add --virtual build-deps \
        bash g++ freetype-dev libpng-dev make \
        ncurses-dev openblas-dev readline-dev \
 && cat requirements.txt | xargs -n 1 pip3 install \
 && sed -i '912s/nam\-e/name/' \
        /usr/local/lib/python3.6/site-packages/networkit/profiling/profiling.py \
 && apk del build-deps

RUN apk --no-cache add libgomp libstdc++ openblas xvfb

RUN mkdir /data
COPY data/paper-features.csv /data/paper-features.csv
RUN chmod -R 777 /data
COPY src /src

WORKDIR /src
CMD main.py


FROM nemo-eva as nemo-eva-dev

RUN pip3 install pycodestyle pytest pytest-ordering
