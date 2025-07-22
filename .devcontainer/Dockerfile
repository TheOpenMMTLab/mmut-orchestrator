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
RUN pip3 install docker
RUN pip3 install prefect
RUN pip3 install rdflib
RUN pip3 install networkx
RUN pip3 install git+https://github.com/dfriedenberger/obse.git
RUN pip3 install git+https://github.com/dfriedenberger/mmut-rdf-model.git

# prefect server shouls be accessible from outside the container
ENV PREFECT_API_HOST=0.0.0.0
ENV PREFECT_API_URL=http://127.0.0.1:4200/api






