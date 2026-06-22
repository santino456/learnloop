#!/bin/bash
# Start the ACP sample course with LearnLoop.

set -e
cd "$(dirname "$0")/../.."

python3 -m learnloop serve courses/acp-fundamentals "$@"
