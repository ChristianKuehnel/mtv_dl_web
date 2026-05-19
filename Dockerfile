FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MTV_DL_WEB_CONFIG=/config/mtv_dl_web.yaml

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 mtvdlweb \
    && useradd --uid 10001 --gid mtvdlweb --home-dir /app --shell /usr/sbin/nologin --no-create-home mtvdlweb

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

RUN mkdir -p /config /downloads /database \
    && chown -R mtvdlweb:mtvdlweb /app /config /downloads /database

VOLUME ["/config", "/downloads", "/database"]
EXPOSE 8071

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent --show-error http://127.0.0.1:8071/health >/dev/null || exit 1

USER mtvdlweb

CMD ["python", "-m", "mtv_dl_web.server"]
