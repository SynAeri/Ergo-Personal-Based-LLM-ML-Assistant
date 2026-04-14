#!/usr/bin/env bash
# Start Ergo orchestrator with required library path
# Run this before using Ergo in Neovim

cd "$(dirname "$0")"

# libstdc++ required by grpc on NixOS — gcc-14.3.0-lib in nix store
export LD_LIBRARY_PATH=/nix/store/4igvzjcy5363yss9cails1g8m5i1bp78-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH

# Activate venv and start orchestrator
source orchestrator/venv/bin/activate
python -m orchestrator.src.main
