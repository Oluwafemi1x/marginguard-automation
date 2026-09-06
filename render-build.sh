#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt
python -m playwright install chromium
