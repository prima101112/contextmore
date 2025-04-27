#!/bin/bash
# this is a script to run qdrant in a container in your local machine.
# it will mount the qdrant/data directory to the container and run the container.

mkdir -p qdrant/data
docker run -it -d -p 6333:6333 \
    -v $(pwd)/qdrant/data:/qdrant/storage \
    qdrant/qdrant