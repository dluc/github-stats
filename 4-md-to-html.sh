#!/usr/bin/env bash
# Author: Devis Lucato, https://github.com/dluc

set -e

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/"

grip --gfm report.md --export report.html
