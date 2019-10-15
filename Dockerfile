FROM alpine
RUN apk add --update python3-dev py3-cffi gcc linux-headers musl-dev sqlite
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install html5lib
RUN pip3 install passlib
RUN pip3 install argon2_cffi
RUN pip3 install translitcodec
RUN pip3 install waitress
RUN pip3 install feedparser
#RUN pip3 install yappi
COPY . /temboz
RUN rm -f /temboz/tembozapp/feedparser.py
VOLUME ["/temboz/data"]
WORKDIR /temboz/data
ENV DOCKER=true
EXPOSE 9999/tcp
ENTRYPOINT ["python3", "-v", "/temboz/temboz", "--server"]
