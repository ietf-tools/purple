FROM node:24 AS build
WORKDIR /workspace
COPY ./client ./
RUN npm ci && \
    npm run build

FROM node:24
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"
WORKDIR /workspace
COPY --from=build /workspace/.output .
ENV NITRO_PORT=3000
CMD ["node", "server/index.mjs"]
EXPOSE 3000
