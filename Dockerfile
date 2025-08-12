FROM python:3.10
WORKDIR /workspace

RUN apt-get update

RUN mkdir -p /workspace/ifc_storage
RUN useradd -m appuser
RUN chown -R appuser:appuser /workspace

COPY src /workspace/src
COPY requirements.txt /workspace/requirements.txt
COPY config.yml /workspace/config.yml
COPY sql /workspace/sql

RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt

USER appuser