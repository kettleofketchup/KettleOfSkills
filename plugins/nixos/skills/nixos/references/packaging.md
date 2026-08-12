# Nix Packaging Reference

## stdenv.mkDerivation

```nix
{ lib, stdenv, fetchFromGitHub }:

stdenv.mkDerivation {
  pname = "mypackage";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "owner";
    repo = "repo";
    rev = "v${version}";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  # Build-time only dependencies
  nativeBuildInputs = [ ];

  # Runtime and compile-time dependencies
  buildInputs = [ ];

  # Build phases (all optional, have defaults)
  configurePhase = ''
    runHook preConfigure
    # custom configure
    runHook postConfigure
  '';

  buildPhase = ''
    runHook preBuild
    make
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin
    cp myapp $out/bin/
    runHook postInstall
  '';

  meta = {
    description = "Description";
    homepage = "https://example.com";
    license = lib.licenses.mit;
    maintainers = [ ];
    platforms = lib.platforms.linux;
  };
}
```

## Fetchers

```nix
# GitHub release
fetchFromGitHub {
  owner = "owner";
  repo = "repo";
  rev = "v1.0.0";
  hash = "sha256-...";
}

# GitLab (including self-hosted)
fetchFromGitLab {
  domain = "gitlab.example.com";  # optional, defaults to gitlab.com
  owner = "group";
  repo = "project";
  rev = "abc123";
  hash = "sha256-...";
}

# URL
fetchurl {
  url = "https://example.com/file.tar.gz";
  hash = "sha256-...";
}

# Zip/tarball with auto-extract
fetchzip {
  url = "https://example.com/archive.zip";
  hash = "sha256-...";
}

# Git repository
fetchgit {
  url = "https://github.com/owner/repo";
  rev = "abc123";
  hash = "sha256-...";
}
```

## Getting Hashes

```bash
# Prefetch URL
nix-prefetch-url https://example.com/file.tar.gz

# Prefetch and unpack
nix-prefetch-url --unpack https://example.com/archive.tar.gz

# Prefetch GitHub
nix-prefetch-github owner repo --rev v1.0.0

# From failed build (shows expected hash)
nix build 2>&1 | grep 'got:' | awk '{print $2}'

# SRI format (preferred)
nix hash to-sri --type sha256 <hash>
```

## runCommand (Simple Derivations)

```nix
# Basic command
pkgs.runCommand "name" {} ''
  echo "hello" > $out
''

# With dependencies
pkgs.runCommand "name" {
  buildInputs = [ pkgs.jq ];
} ''
  echo '{"a":1}' | jq '.a' > $out
''

# With source files
pkgs.runCommand "name" {
  src = ./source;
} ''
  cp -r $src $out
''
```

Continued in `packaging-images.md`.
