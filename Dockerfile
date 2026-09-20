# syntax=docker/dockerfile:1.7
# Tiny backend that reports which replica answered, so load balancing is visible.

FROM python:3.12-alpine

RUN adduser -D -H -u 10001 app
WORKDIR /app
COPY --chown=10001:10001 app.py .

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/healthz || exit 1

CMD ["python", "app.py"]
