#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=== Data Quality & AI/LLM Testing Suite: Running All Tests ==="
python3 test_runner.py
