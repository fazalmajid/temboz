FROM alpine
RUN apk add --update python3-dev py3-cffi gcc linux-headers musl-dev sqlite
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
COPY . /temboz
RUN pip3 install -r /temboz/tembozapp/requirements.txt
RUN rm -f /temboz/tembozapp/feedparser.py
VOLUME ["/temboz/data"]
WORKDIR /temboz/data
ENV DOCKER=true
EXPOSE 9999/tcp
ENTRYPOINT ["python3", "/temboz/temboz", "--server"]
