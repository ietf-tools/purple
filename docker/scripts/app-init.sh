#!/bin/bash

cd /workspace

# Add /workspace as a safe git directory
git config --global --add safe.directory /workspace

# Turn off git info in zsh prompt (causes slowdowns)
git config oh-my-zsh.hide-info 1

# Try to fetch datatracker API schema and build the client
echo "Fetching datatracker API schema..."
if wget -O rpcapi.yaml http://host.docker.internal:8000/api/schema/; then
    echo "Building datatracker API client..."
    client/node_modules/.bin/openapi-generator-cli generate  --generator-key datatracker # config in openapitools.json
    /bin/cp rpcapi.yaml openapi/rpcapi_client/.rpcapi.yaml
    BUILT_API=yes
else
    echo "...API schema fetch failed"
fi

# Install requirements.txt dependencies
echo "Installing dependencies from requirements.txt..."
pip3 --disable-pip-version-check --no-cache-dir install --user --no-warn-script-location -r requirements.txt

# Run nginx
echo "Starting nginx..."
sudo nginx

# Wait for DB container
echo "Waiting for DB container to come online..."
/usr/local/bin/wait-for db:5432 -- echo "PostgreSQL ready"

# Install client dependencies
cd client
npm install
cd ..

# Run migrations
echo "Running migrations..."
./manage.py migrate --no-input || true

echo "Populating initial history..."
./manage.py populate_history --auto || true

# Collect statics
./manage.py collectstatic --no-input || true

# Django should be operational now. Build purple API client.
./manage.py spectacular --file purple_api.yaml && \
    client/node_modules/.bin/openapi-generator-cli generate --generator-key purple  || true
    /bin/cp purple_api.yaml client/app/purple_client/.purple_api.yaml

sudo touch /.dev-ready

if [ -z "$EDITOR_VSCODE" ]; then
  echo "-----------------------------------------------------------------"
  echo "Ready!"
  echo "-----------------------------------------------------------------"
  echo "Launching tmux..."

  tmux start-server
  tmux new-session -d -s dev -c '/workspace'
  sleep 1
  if [[ "$BUILT_API" == "yes" ]]; then
      tmux send-keys './manage.py runserver 8001' Enter
  else
      tmux send-keys '# Unable to fetch datatracker API schema during initialization.' Enter
      tmux send-keys '# Ensure your datatracker dev instance is running and execute ./update-rpcapi,' Enter
      tmux send-keys '# then run pip install -r requirements.txt, and finally ./manage.py runserver 8001' Enter
  fi
  tmux split-window -h -c '/workspace/client'
  tmux send-keys 'npm run dev' Enter
  tmux -2 attach-session -d -c '/workspace'

  echo "You've exited tmux. Send "exit" to stop the containers and quit."
  zsh
  exit 0
fi
