FROM python:3.10
WORKDIR /workspace
COPY libs /workspace/libs
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /workspace/requirements.txt
COPY src /workspace/src
COPY config.yml /workspace/config.yml

CMD [ "python", "src/main.py"]