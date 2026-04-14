{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Ergo-specific dependencies — Hyprland native, no xdotool needed
    hyprland
    pkg-config
    openssl
    openssl.dev
    stdenv.cc.cc.lib  # libstdc++ for grpc in Python venv
  ];

  OPENSSL_DIR = "${pkgs.openssl.dev}";
  OPENSSL_LIB_DIR = "${pkgs.openssl.out}/lib";

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Ergo Development Environment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Available commands:"
    echo "  cargo build  - Build Ergo"
    echo "  cargo run    - Run Ergo"
    echo "  cargo test   - Run tests"
    echo ""
    echo "libstdc++: ${pkgs.stdenv.cc.cc.lib}/lib"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  '';
}
