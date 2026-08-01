#!/bin/bash
set -e

# Run main script directly which auto-detects an open port if standard ports are in use
exec python3 -m app.main
