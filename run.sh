#!/usr/bin/env bash
# Author: Devis Lucato, https://github.com/dluc

set -e

PATH="$PATH:/snap/bin/"

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/"

source .env

echo "Downloading PRs..." > last-run.log
./1-download-json.sh

echo "JSON to CSVs..." > last-run.log
./2-update-csv.sh

echo "Gen report..." > last-run.log
./3-gen-stats.sh

cat report.md | gh gist edit $GIST report.md
