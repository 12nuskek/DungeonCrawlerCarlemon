# F02 build/test environment; ROMs stay inside local container/artifacts only.
FROM debian:13.6-slim@sha256:d7e12182ce18b85b93007c1dedf31f2d29e01ccf3182cc4017c709b6259bc132
# Public trust roots supplied by the launcher support managed-network proxies.
COPY --chmod=0644 host-ca.crt /opt/build-ca.crt
ENV GIT_SSL_CAINFO=/opt/build-ca.crt
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::https::CaInfo=/opt/build-ca.crt update \
    && apt-get -o Acquire::https::CaInfo=/opt/build-ca.crt install -y --no-install-recommends \
    build-essential binutils-arm-none-eabi ca-certificates git libpng-dev \
    pkg-config libmgba-dev python3-pil \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
