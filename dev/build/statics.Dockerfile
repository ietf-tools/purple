FROM ghcr.io/ietf-tools/purple-backend:latest AS builder

 # Collect statics
RUN PURPLE_DEPLOYMENT_MODE=build ./manage.py collectstatic --no-input


FROM nginx:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

COPY --from=builder /workspace/purple/static /usr/share/nginx/html/static/

