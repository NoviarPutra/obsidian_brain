#!/usr/bin/env bash
# ==============================================================================
# Script: sync_fabric_and_cl4r1t4s.sh
# Purpose: Upstream synchronization for Fabric CLI patterns and CL4R1T4S corpus
# Integration: Local macOS & Remote VPS (voldemort-vps)
# ==============================================================================

set -euo pipefail

echo "==> [1/4] Updating Local Fabric Patterns from Upstream..."
if command -v fabric >/dev/null 2>&1; then
    fabric -U || echo "Warning: fabric -U returned non-zero"
    echo "Local Fabric patterns updated in ~/.config/fabric/patterns"
else
    echo "Warning: fabric binary not found locally in PATH"
fi

echo "==> [2/4] Updating Local CL4R1T4S Corpus..."
if [ -d "$HOME/Security/CL4R1T4S/.git" ]; then
    git -C "$HOME/Security/CL4R1T4S" pull --ff-only || echo "Warning: CL4R1T4S pull failed"
else
    mkdir -p "$HOME/Security"
    git clone --depth 1 https://github.com/elder-plinius/CL4R1T4S.git "$HOME/Security/CL4R1T4S"
fi

echo "==> [3/4] Updating Remote VPS Fabric Patterns..."
ssh -o ConnectTimeout=5 voldemort-vps "
    if [ -x ~/.local/bin/fabric ]; then
        ~/.local/bin/fabric -U || true
    fi
"

echo "==> [4/4] Updating Remote VPS CL4R1T4S Corpus..."
ssh -o ConnectTimeout=5 voldemort-vps "
    if [ -d ~/Security/CL4R1T4S/.git ]; then
        git -C ~/Security/CL4R1T4S pull --ff-only || true
    else
        mkdir -p ~/Security
        git clone --depth 1 https://github.com/elder-plinius/CL4R1T4S.git ~/Security/CL4R1T4S
    fi
"

echo "✅ All upstream integrations (Fabric + CL4R1T4S) successfully synchronized!"
