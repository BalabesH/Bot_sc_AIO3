FROM python:3.10.10

ENV http_proxy
ENV https_proxy
# Install system dependencies
WORKDIR /src
USER root
RUN  export http_proxy= \
    && export https_proxy=\
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc git \
    && apt-get install -yqq --no-install-recommends \
    freetds-bin \
    build-essential \
    default-libmysqlclient-dev \
    apt-utils \
    curl \
    vim \
    rsync \
    netcat \
    locales \
    libaio1 \
    freetds-dev \
    libkrb5-dev \
    libsasl2-dev \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libzbar-dev

COPY requirements.txt /src
COPY . /src
COPY ./proxy /etc/apt/apt.conf.d/proxy
COPY ./instant12.tar /instant12.tar



RUN mkdir -p /opt/oracle \
    && cp instant12.tar /opt/oracle \
    && cd /opt/oracle \
    && tar -xf instant12.tar \
    && cd /opt/oracle/instantclient_12_2 \
    && ln -s libclntsh.so.12.1 libclntsh.so \
    && ln -s libocci.so.12.1 libocci.so \
    && ldconfig \
    && sh -c "echo /opt/oracle/instantclient_12_2 > /etc/ld.so.conf.d/oracle-instantclient.conf" \
    && ldconfig \
    && mkdir -p /opt/oracle/instantclient_12_2/network/admin \
    && export PATH=/opt/oracle/instantclient_12_2:$PATH

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

# RUN apt-get update && apt-get install -y libpq-dev \
#     gcc

RUN pip install --proxy --no-cache-dir -r requirements.txt
# RUN apt-get update && apt-get install libzbar0 -y && pip install --proxy http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 pyzbar
