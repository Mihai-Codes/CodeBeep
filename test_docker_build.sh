#!/bin/bash
set -e

echo "Building CodeBeep Docker image..."
docker build -t codebeep:latest .

echo "Testing Docker run..."
docker run --rm \
  -e MATRIX_HOMESERVER=https://matrix.beeper.com \
  -e MATRIX_USERNAME=test \
  -e MATRIX_PASSWORD=test \
  -e OPENCODE_SERVER_URL=http://host.docker.internal:4096 \
  codebeep:latest --help

echo "Docker build successful!"