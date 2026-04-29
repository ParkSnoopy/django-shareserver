FROM debian:13-slim

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

USER root

RUN \
	apt update -y				&&\
	apt install -y python3 python3-pip	&&\
	rm -rf /var/lib/apt/lists/*		&&\
	python3 -m pip install --break-system-packages uv

COPY . /app

ENTRYPOINT ["/app/entrypoint.sh"]
