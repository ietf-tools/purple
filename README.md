<div align="center">

<img src="https://raw.githubusercontent.com/ietf-tools/common/main/assets/logos/rpc.svg" alt="RPC" height="125" />

<!-- [![Release](https://img.shields.io/github/release/ietf-tools/rpc.svg?style=flat&maxAge=300)](https://github.com/ietf-tools/rpc/releases) -->
[![License](https://img.shields.io/github/license/ietf-tools/rpc)](https://github.com/ietf-tools/rpc/blob/main/LICENSE)
![Python Version](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![Django Version](https://img.shields.io/badge/django-5.0-teal?logo=django&logoColor=white)
![Node Version](https://img.shields.io/badge/node.js-22-green?logo=node.js&logoColor=white)
![Nuxt Version](https://img.shields.io/badge/nuxt-3-green?logo=nuxt.js&logoColor=white)
![Vue Version](https://img.shields.io/badge/vue-3-green?logo=vue.js&logoColor=white)

##### Web tool for the RFC Production Center

</div>

- [**Production Website**](https://rpc.ietf.org)
- [Changelog](https://github.com/ietf-tools/rpc/releases)
- [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md)
- [Development](#development)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
  - [Using VS Code](#using-vs-code)
  - [Using Generic](#using-generic)
  - [Commands](#commands)
  - [Cleanup](#cleanup)

# Development

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) *(Windows only)*

## Getting Started

1. Clone this repository locally.
2. Clone the [ietf-tools/datatracker](https://github.com/ietf-tools/datatracker) repository into another directory. Check out the `feat/rpc-api` branch, start the Docker environment, and start the dev server.
3. Continue using the steps for your preferred IDE:
   - [Visual Studio Code](#using-vs-code)
   - [Generic](#using-generic)
4. [Create demo data](#create-demo-data) if you have not already

## Using VS Code

1. Open the project in VS Code
2. When prompted, in the lower right corner, click <kbd>Reopen in container</kbd>
3. Wait for the devcontainer to initialize. *(This can take a few seconds/minutes the first time)*
4. The editor will automatically open 2 side-by-side terminals, running both the backend API server and the client dev server.
5. Open http://localhost:8088 in your browser and login using some Datatracker user.

## Using Generic

1. In a terminal, from the project root folder, run the command:
    ```sh
    docker/run
    ```
2. Wait for the containers to initialize. *(This can take a few seconds/minutes the first time)*
3. A tmux session will automatically be started with the backend API server running on the left and the client dev server running on the right.
4. Open http://localhost:8088 in your browser and login using some Datatracker user.

#### Tips

- The tmux default prefix binding is set to `Ctrl+Space` and mouse control is enabled by default.
- If you exit tmux, you'll land in a normal zsh prompt. Type `exit` again to quit and stop the containers.

## Commands

#### Django Backend API (`/workspace`)

- Start Server: `./manage.py runserver 8001`

#### Nuxt Client (`/workspace/client`)

- Run Dev Server: `npm run dev`
- Generate Production Build: `npm run build`

## Create demo data

To create demo data, open an app container shell and run the management command
```sh
./manage.py create_rpc_demo
```
This requires that the Datatracker dev server be running.

To remove all data and start afresh, you can run
```sh
./manage.py purge --yes-im-sure
```
and all data in the RPC tool's database will be reset. The Datatracker _will not_ be reset, but running `create_rpc_demo` again will work as intended.

## APIs

This project uses two distinct HTTP APIs. Both are accessed using clients generated from OpenAPI specifications. The clients are generated using [OpenAPI Generator](https://openapi-generator.tech/).

### Front-end to Back-end: `purple_api`

This API is used by the Nuxt Client front end to communicate with the Django back end. This API is defined by this project through an OpenAPI specification in `purple_api.json`. The API is implemented using the `django-rest-framework` and the spec is generated using `drf-spectacular`.

### Back-end to Datatracker: `rpcapi`

This API is used by the Django back end to communicate with the Datatracker. It is implemented in the Datatracker code and described (as of Jan 2024) by a hand-written OpenAPI spec in `rpcapi.json`. The current version of the spec is fetched from the Datatracker's `feat/rpc-api` branch when starting this project's Docker environment. If the API is updated on the Datatracker side, you must manually copy the new `rpcapi.json` into the root of this project and update the clients as described in the next section.

### Updating the API clients

If changes are made to the APIs, you will need to update the clients. If this includes changes to the Datatracker's `rpcapi.json` file you must first copy the new version of that file into this project's root. Then, from inside this project's Docker shell, run
```sh
./update-rpcapi
```
This uses [OpenAPI Generator](https://openapi-generator.tech/) to regenerate `purple_api.json` and builds both the API clients. It may take a minute or two. When it is done, restart the Django dev server. The Nuxt server normally picks up the changes automatically.

## Cleanup

To fully tear down the containers created in either of the VS Code or Generic steps, run the following command from the project root folder:
```sh
docker/cleanall
```
Press <kbd>Y</kbd> to confirm.
