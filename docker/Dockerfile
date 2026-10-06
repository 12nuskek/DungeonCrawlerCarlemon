# F02 build/test environment; ROMs stay inside local container/artifacts only.
FROM debian:13.6-slim@sha256:d7e12182ce18b85b93007c1dedf31f2d29e01ccf3182cc4017c709b6259bc132
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential binutils-arm-none-eabi ca-certificates git libpng-dev \
    pkg-config libmgba-dev python3-pil \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
