#!/bin/bash
export AZURE_STORAGE_ACCOUNT=ietfbackup
az login

echo "Fetching latest xfer dump..."
LATESTDBKEY=$(az storage blob list -c database --prefix purple/purple --query "[-1:].name | [0]" --out tsv)
az storage blob download -c database -n $LATESTDBKEY -f .db-dump/purple.dump -o none
