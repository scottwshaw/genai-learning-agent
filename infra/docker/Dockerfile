FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends jq git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir anthropic

WORKDIR /workspace
