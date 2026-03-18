# Ergo - Local-first NixOS personal operator
# Full development and runtime environment

{
  description = "Ergo: Local-first AI assistant for NixOS with developer context and memory";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };

        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" "rust-analyzer" ];
        };

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          fastapi
          uvicorn
          sqlalchemy
          psycopg2
          httpx
          pydantic
          python-dotenv
          anthropic
          google-generativeai
          openai
          chromadb
          langchain
          numpy
          pandas
        ]);

      in
      {
        packages = {
          # Rust daemon package
          ergo-daemon = pkgs.rustPlatform.buildRustPackage {
            pname = "ergo-daemon";
            version = "0.1.0";
            src = ./.;
            cargoLock.lockFile = ./Cargo.lock;

            nativeBuildInputs = with pkgs; [
              pkg-config
            ];

            buildInputs = with pkgs; [
              sqlite
              xorg.libX11
              xorg.libXi
              xorg.libXtst
            ];
          };

          # Python orchestrator (wrapped script)
          ergo-orchestrator = pkgs.writeShellScriptBin "ergo-orchestrator" ''
            export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
            ${pythonEnv}/bin/python ${./orchestrator/src/main.py} "$@"
          '';

          # UI server
          ergo-ui = pkgs.writeShellScriptBin "ergo-ui" ''
            export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
            ${pythonEnv}/bin/python ${./ui/src/server.py} "$@"
          '';

          default = self.packages.${system}.ergo-daemon;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Rust toolchain
            rustToolchain
            cargo-watch
            cargo-edit

            # Python environment
            pythonEnv

            # System libraries
            pkg-config
            sqlite
            postgresql

            # X11 for window monitoring
            xorg.libX11
            xorg.libXi
            xorg.libXtst

            # Development tools
            ripgrep
            fd
            jq

            # Optional: voice/audio
            # whisper-cpp
            # portaudio
          ];

          shellHook = ''
            echo "Ergo development environment loaded"
            echo "Available commands:"
            echo "  cargo run           - Run the daemon"
            echo "  cargo run -- stats  - Show statistics"
            echo "  python orchestrator/src/main.py - Run orchestrator"
            echo "  python ui/src/server.py - Run UI server"

            # Ensure data directories exist
            mkdir -p ~/.local/share/ergo/{events,session_summaries,screenshots,audio,repo_snapshots,models,backups}
            mkdir -p ~/.config/ergo
          '';
        };

        apps = {
          daemon = {
            type = "app";
            program = "${self.packages.${system}.ergo-daemon}/bin/ergo";
          };

          orchestrator = {
            type = "app";
            program = "${self.packages.${system}.ergo-orchestrator}/bin/ergo-orchestrator";
          };

          ui = {
            type = "app";
            program = "${self.packages.${system}.ergo-ui}/bin/ergo-ui";
          };
        };
      }
    );
}
