FROM alpine
RUN apk add --update python3-dev py3-cffi gcc linux-headers musl-dev sqlite
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
COPY tembozapp/requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . /temboz
RUN rm -f /temboz/tembozapp/feedparser.py
VOLUME ["/temboz/data"]
WORKDIR /temboz/data
ENV DOCKER=true
EXPOSE 9999/tcp
ENTRYPOINT ["python3", "/temboz/temboz", "--server"]
