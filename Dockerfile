FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MTV_DL_WEB_CONFIG=/config/mtv_dl_web.yaml

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

RUN mkdir -p /config /downloads /database

VOLUME ["/config", "/downloads", "/database"]
EXPOSE 8071

CMD ["python", "-c", "from mtv_dl_web.app import create_app; from mtv_dl_web import config; create_app().run(host=config.host, port=config.port)"]
