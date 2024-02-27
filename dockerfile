FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --proxy http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 -r requirements.txt
RUN pip install --upgrade pip
RUN chmod 755 .
COPY . ./app

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

RUN set -ex \
    && buildDeps=' \
    freetds-dev \
    libkrb5-dev \
    libsasl2-dev \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    git \
    ' \
    && export http_proxy=http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 \
    && export https_proxy=http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 \
    && export HTTP_PROXY=http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 \
    && export HTTPS_PROXY=http://ru20003072:Bluntman1!@proxy.ru.auchan.com:3128 \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
    $buildDeps \
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
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    #    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    #    && rm -rf \
    #        /var/lib/apt/lists/* \
    #        /tmp/* \
    #        /var/tmp/* \
    #        /usr/share/man \
    #        /usr/share/doc \
    #        /usr/share/doc-base \
    && mkdir /opt/oracle \
    && cp /instant12.tar /opt/oracle \
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

# # Install ZBar
# RUN apt-get install zbar-tools -y
# RUN apt-get install libzbar-dev -y
# RUN apt-get install python-pip -y
# #RUN pip install —-upgrade pip
# RUN pip install pypng
# RUN pip install zbar
# RUN pip install pillow
# RUN pip install qrtools
RUN apt-get update && apt-get install -y libpq-dev \
    gcc
