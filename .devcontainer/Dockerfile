FROM python:3.12-slim-bookworm


# set timezone to Europ/Berlin
RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata


# Docker cli
RUN apt-get update
RUN apt-get install -y curl git


# Docker CLI installieren
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-28.3.2.tgz | tar xz 
RUN mv docker/docker /usr/local/bin/ 
RUN rm -rf docker

## Pythoin dependencies
RUN pip3 install --upgrade pip
COPY requirements-api.txt /tmp/requirements-api.txt
COPY requirements.txt /tmp/requirements.txt
COPY scripts/shared_checksums.py /usr/local/bin/shared_checksums.py
RUN pip3 install -r /tmp/requirements.txt
RUN chmod +x /usr/local/bin/shared_checksums.py

# prefect server shouls be accessible from outside the container
ENV PREFECT_API_HOST=0.0.0.0
ENV PREFECT_API_URL=http://127.0.0.1:4200/api






