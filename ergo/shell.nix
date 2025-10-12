{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Ergo-specific dependencies
    xdotool
    xorg.libX11
    pkg-config
  ];
  
  shellHook = ''
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Ergo Development Environment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Available commands:"
    echo "  cargo build  - Build Ergo"
    echo "  cargo run    - Run Ergo"
    echo "  cargo test   - Run tests"
    echo ""
    echo "X11 libs: ${pkgs.xorg.libX11}/lib"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  '';
}
