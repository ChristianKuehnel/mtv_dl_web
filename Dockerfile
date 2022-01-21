FROM python:3.9-alpine3.15

RUN mkdir /mtv_dl_web ;\
    mkdir /config ;\
    mkdir /videos

VOLUME /config
VOLUME /videos

# configure timezone
RUN apk update; \
    apk add  --no-cache tzdata; \
    cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime; \
    echo "Europe/Berlin" >  /etc/timezone

# install dependencies
ADD requirements.txt /mtv_dl_web/
RUN pip3 install -r /mtv_dl_web/requirements.txt

# add application
ADD  mtv_dl_web.py index.html /mtv_dl_web/
RUN chmod +x /mtv_dl_web/mtv_dl_web.py

# TODO: configure timezone
# TODO: run as non root
# TODO: let user configure UID/GID via environment
WORKDIR /mtv_dl_web
CMD ["./mtv_dl_web.py"]