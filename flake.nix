{
  description = "nexus";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      # Usage: nix develop
      # All Python deps are managed by uv via pyproject.toml (e.g. uv run src/app.py)
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.uv
        ];
        # Needed for native extensions (psycopg2, tiktoken, etc.)
        env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
          pkgs.stdenv.cc.cc.lib
          pkgs.libz
        ];
      };
    };
}
