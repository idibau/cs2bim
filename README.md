# cs2bim

## Getting started dev

Build and run docker container or build and open cotainer with VSCode
```console
docker-compose -f docker-compose-dev.yml up 
```
Install pip packages (Run in container at /workspace)
```console
pip install --no-cache-dir --upgrade -r /workspace/requirements.txt
```