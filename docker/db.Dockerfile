FROM postgres:17
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

COPY docker/scripts/db-import.sh /docker-entrypoint-initdb.d/

ENV DUMPFILE=""
