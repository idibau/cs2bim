FROM python:3.10

LABEL org.opencontainers.image.source="https://github.com/idibau/cs2bim"

WORKDIR /workspace

RUN apt-get update

RUN useradd -m appuser
RUN chown -R appuser:appuser /workspace

RUN mkdir /workspace/ifc
RUN chown -R appuser:appuser /workspace/ifc
RUN mkdir /workspace/cache
RUN chown -R appuser:appuser /workspace/cache
RUN mkdir /workspace/logs
RUN chown -R appuser:appuser /workspace/logs

COPY src /workspace/src
COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

USER appuser