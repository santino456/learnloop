#!/bin/bash
# Validate and build the ACP sample course.

set -e
cd "$(dirname "$0")/../.."

echo "=== LearnLoop ACP course check ==="
python3 -m learnloop validate courses/acp-fundamentals
python3 -m learnloop build courses/acp-fundamentals
echo "OK"
