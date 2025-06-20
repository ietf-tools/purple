FROM ghcr.io/ietf-tools/purple-backend:latest AS builder

 # Collect statics
RUN PURPLE_DEPLOYMENT_MODE=build ./manage.py collectstatic --no-input

FROM ghcr.io/nginxinc/nginx-unprivileged:1.27
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

# install the static files
COPY --from=builder /workspace/purple/static /usr/share/nginx/html/static/

# listen on port 8042 instead of 8080
RUN sed --in-place 's/8080/8042/' /etc/nginx/conf.d/default.conf
