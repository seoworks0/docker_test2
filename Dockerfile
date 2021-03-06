FROM intimatemerger/mecab-python:0.996-alpine

LABEL maintainer "mats116 <mats.kazuki@gmail.com>"

COPY mecabrc /usr/local/etc/mecabrc

RUN apk add --no-cache --virtual=build-deps git bash curl file openssl sudo perl && \
    git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git /tmp/neologd && \
    /tmp/neologd/bin/install-mecab-ipadic-neologd -n -y && \
    apk del build-deps && \
    rm -rf /tmp/neologd

CMD ["/usr/local/bin/mecab"]

FROM python
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN apt-get update && apt-get install -y
RUN apt-get install libmecab-dev
RUN pip3 install --upgrade pyzmq --install-option="--zmq=bundled" && \
    pip3 install --upgrade jupyter && \
    pip3 install --upgrade \
    numpy \
    scipy \
    scikit-learn \
    matplotlib \
    pandas \
    mecab-python3 \
    neologdn
RUN pip install -r requirements.txt
ADD . /code/
