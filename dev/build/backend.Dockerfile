FROM ghcr.io/ietf-tools/purple-app-base:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1000 rpc && \
    useradd -c "Purple People Eater" -u 1000 -g rpc -m -s /bin/false purple

COPY . .
COPY ./dev/build/start.sh ./start.sh
COPY ./dev/build/backend-start.sh ./backend-start.sh
COPY ./dev/build/celery-start.sh ./celery-start.sh
COPY ./dev/build/migration-start.sh ./migration-start.sh
COPY ./dev/build/gunicorn.conf.py ./gunicorn.conf.py

RUN pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt

# Generate Purple openapi schema
RUN PURPLE_DEPLOYMENT_MODE=build ./manage.py spectacular --file purple_api.yaml --validate # --fail-on-warn (when we can)

RUN chmod +x start.sh && \
    chmod +x backend-start.sh && \
    chmod +x migration-start.sh

CMD ["./start.sh"]

EXPOSE 8000
