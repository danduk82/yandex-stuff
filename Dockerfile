FROM ubuntu:24.04


SHELL ["/bin/bash", "-o", "pipefail", "-cux"]
ENV \
    DEBIAN_FRONTEND=noninteractive \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
RUN \
    . /etc/os-release && \
    apt-get update && \
    apt-get --assume-yes upgrade && \
    apt-get clean

RUN apt-get update -q && \
    apt-get install --no-install-recommends -yq \
        sudo     \
        vim      \
        wget     \
        curl     \
        less     \
        iproute2 \
        python3-pip  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*


COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages  -r /tmp/requirements.txt
RUN pip3 install --break-system-packages  ipython geoservercloud


COPY scripts /scripts
COPY stats /stats
COPY stats/yandex-stats.py /usr/local/bin/yandex-stats
RUN chmod +x /usr/local/bin/yandex-stats

VOLUME [ "/workdir" ]
WORKDIR /workdir