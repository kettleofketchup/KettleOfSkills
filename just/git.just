set shell := ["bash", "-euo", "pipefail", "-c"]

# Bump version, sync, commit, and tag a release
[no-cd]
[group('git')]
version bump:
    #!/usr/bin/env bash
    set -euo pipefail

    current="$(cat VERSION | tr -d '[:space:]')"
    IFS='.' read -r major minor patch <<< "$current"

    case "{{bump}}" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        hotfix|patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Usage: just git::version <major|minor|hotfix>"
            echo "  Current version: ${current}"
            exit 1
            ;;
    esac

    new="${major}.${minor}.${patch}"
    echo "Bumping version: ${current} -> ${new}"

    # Update VERSION file
    echo "$new" > VERSION

    # Run full sync (groups + marketplace)
    just sync

    # Stage and commit
    git add VERSION .claude-plugin/marketplace.json plugins/
    git commit -m "release: v${new}"

    # Tag
    git tag "v${new}"

    echo ""
    echo "Tagged v${new}"
    echo "Run 'git push origin main --tags' to publish"
