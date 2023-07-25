#!/usr/bin/env bash
# Author: Devis Lucato, https://github.com/dluc

set -e

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/"

python -c "from lib import gen_report; gen_report()" > report.md
