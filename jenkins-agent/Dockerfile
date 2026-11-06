FROM jenkins/agent:latest-jdk25

USER root
COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /usr/local/bin/

USER jenkins
ENV UV_CACHE_DIR=/home/jenkins/.cache/uv
RUN uv python install 3.12

# push docker image docker push hmchan4/hybridrag-jenkin-agent:latest
