FROM ubuntu:latest
LABEL authors="aller"

ENTRYPOINT ["top", "-b"]