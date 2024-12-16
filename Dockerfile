FROM ubuntu:latest
LABEL authors="markc"

ENTRYPOINT ["top", "-b"]