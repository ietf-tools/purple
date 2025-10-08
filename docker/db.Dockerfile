# =====================
# --- Builder Stage ---
# =====================
FROM postgres:17 AS builder

ENV POSTGRES_PASSWORD=abcd1234
ENV POSTGRES_USER=rpc
ENV POSTGRES_DB=rpctools
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV PGDATA=/data

COPY docker/scripts/db-import.sh /docker-entrypoint-initdb.d/
COPY purple.dump /

RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

# ===================
# --- Final Image ---
# ===================
FROM postgres:17
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

COPY --from=builder /data $PGDATA

ENV POSTGRES_PASSWORD=abcd1234
ENV POSTGRES_USER=rpc
ENV POSTGRES_DB=rpctools
ENV POSTGRES_HOST_AUTH_METHOD=trust
