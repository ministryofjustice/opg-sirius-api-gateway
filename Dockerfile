FROM python:alpine

COPY ./docker /srv/docker

WORKDIR /srv/docker

# For managing containers from within this container.
RUN apk add docker

# Mock Gateway Python dependenciaes
RUN pip install -r api-gateway/requirements.txt

ENV FLASK_APP api-gateway/start.py
ENV FLASK_DEBUG 1

RUN chmod +x ./start.sh
ENTRYPOINT ["./start.sh"]
