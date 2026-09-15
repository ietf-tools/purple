#!/bin/bash
#
# Regenerate the purple OpenAPI schema (purple_api.yaml) and the generated
# TypeScript client (client/app/purple_client/) from the CURRENT Django code.
#
# The generated client is gitignored, so it does NOT survive a container
# rebuild and must be rebuilt from the running code. This is also the recovery
# path whenever the frontend reports "api.<something> is not a function": that
# error means the generated client is out of sync with the backend. Safe to
# re-run any time (e.g. after a rebuild or a branch switch).

set -o pipefail
cd /workspace || exit 1

echo "Regenerating purple API schema from Django..."
if ! ./manage.py spectacular --file purple_api.yaml; then
    echo "ERROR: 'manage.py spectacular' failed — purple_api.yaml NOT updated." >&2
    echo "       Refusing to rebuild the client from a stale schema. Fix the" >&2
    echo "       backend, then re-run docker/scripts/build-purple-client.sh." >&2
    exit 1
fi

echo "Generating purple TypeScript client..."
if ! npx --yes @openapitools/openapi-generator-cli@2.29 generate --generator-key purple; then
    echo "ERROR: openapi-generator failed — client/app/purple_client may be stale." >&2
    exit 1
fi

# The generator strips it; @ts-nocheck avoids type errors from generated code.
if ! grep -q "// @ts-nocheck" client/app/purple_client/runtime.ts; then
    sed -i '1i // @ts-nocheck' client/app/purple_client/runtime.ts
fi

# Keep a copy of the exact schema the client was built from.
mkdir -p client/app/purple_client
cp purple_api.yaml client/app/purple_client/.purple_api.yaml

# Sanity check: every operationId in the schema should have a matching method
# in the client (schema is snake_case, client methods are camelCase). This is
# what catches the "... is not a function" class of drift before runtime does.
missing=0
while read -r op; do
    method="$(echo "$op" | sed -E 's/_([a-z])/\U\1/g')"
    if ! grep -q "$method" client/app/purple_client/apis/PurpleApi.ts; then
        echo "WARNING: operation '$op' -> '$method' is missing from the generated client." >&2
        missing=1
    fi
done < <(grep -oE 'operationId: [A-Za-z0-9_]+' purple_api.yaml | awk '{print $2}' | sort -u)

if [ "$missing" -ne 0 ]; then
    echo "WARNING: purple client is OUT OF SYNC with purple_api.yaml (see above)." >&2
    exit 1
fi

echo "purple client is in sync with the schema."
