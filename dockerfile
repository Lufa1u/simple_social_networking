FROM python:3.11

SHELL ["/bin/bash", "-c"]

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update

RUN useradd -rms /bin/bash social_network && chmod 777 /opt /run

WORKDIR /simple_social_networking

COPY --chown=simple_social_networking:simple_social_networking . .

RUN pip install -r requirements.txt

USER social_network