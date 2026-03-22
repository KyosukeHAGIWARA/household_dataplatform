{
  description = "Local household data platform dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = false;
        };
        python = pkgs.python312;
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python
            python312Packages.pip
            python312Packages.virtualenv
            uv
            duckdb
            nodejs_22
            wrangler
            jq
            just
          ];

          shellHook = ''
            export UV_PROJECT_ENVIRONMENT=.venv

            if [ ! -d .venv ]; then
              echo "Creating Python virtual environment (.venv)..."
              uv venv
            fi

            source .venv/bin/activate

            if [ -f pyproject.toml ]; then
              echo "Syncing Python dependencies with uv..."
              uv sync
            fi

            echo "✅ Dev shell ready"
            echo "- Streamlit: streamlit run dashboard-front/app/main.py"
            echo "- Fetch CSV: python dashboard-front/src/fetch_csv.py"
            echo "- Wrangler: (cd depot-server && wrangler dev)"
          '';
        };
      });
}
