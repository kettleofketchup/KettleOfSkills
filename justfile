set shell := ["bash", "-euo", "pipefail", "-c"]

# Run sync-groups then sync-marketplace
sync: sync-groups sync-marketplace

# For each plugin's config.yaml, read categories and create group plugin dirs with symlinks
sync-groups:
    #!/usr/bin/env bash
    set -euo pipefail

    declare -A group_descriptions=(
        [all]="All skills — the complete collection"
        [k8s-core]="Kubernetes core infrastructure — helm, kustomize, argocd, k3s, talos, calico, cert-manager, traefik, kubectx"
        [k8s-storage]="Kubernetes storage — rook-ceph, cloudnative-pg"
        [k8s-apps]="Kubernetes applications — authentik, cloudflare, nextcloud, grafana, opentelemetry, openwebui, and more"
        [homelab]="Homelab infrastructure — nixos, vsphere, k3s, talos, pikvm, and more"
        [devops]="DevOps tooling — docker, github, gitlab-ci, goss, and more"
        [frontend]="Frontend development — react, zustand, ui-styling, playwright, svg-logo-designer"
        [golang]="Go development — golang-viper, go-dota2-steam, wails"
        [docs]="Documentation — mkdocs, mermaidjs, zensical, documentation-reviewer"
        [claude-tooling]="Claude Code tooling — claude-code, context-engineering, mcp-management, skill-creator"
        [shell]="Shell tooling — zinit-zsh, zsh-completions"
        [discord]="Discord bot development"
    )

    valid_groups=("${!group_descriptions[@]}")

    # Clean existing group symlinks (preserve individual plugin dirs that share a group name)
    for group in "${valid_groups[@]}"; do
        if [[ -d "plugins/${group}/skills" ]]; then
            # Only remove symlinks, not real skill directories
            for link in "plugins/${group}/skills"/*; do
                [[ -L "$link" ]] && rm -f "$link"
            done
        fi
    done

    # Iterate over individual plugin config.yaml files
    for config in plugins/*/skills/*/config.yaml; do
        [[ -f "$config" ]] || continue

        # Extract plugin and skill name from path: plugins/<plugin>/skills/<skill>/config.yaml
        plugin="$(echo "$config" | cut -d/ -f2)"
        skill="$(echo "$config" | cut -d/ -f4)"

        # Every skill goes into the "all" group
        mkdir -p "plugins/all/skills"
        if [[ ! -L "plugins/all/skills/${skill}" ]]; then
            ln -s "../../${plugin}/skills/${skill}" "plugins/all/skills/${skill}"
        fi

        # Read categories from config.yaml (lines under "categories:" until next key)
        in_categories=false
        while IFS= read -r line; do
            if [[ "$line" =~ ^categories: ]]; then
                in_categories=true
                continue
            fi
            if $in_categories; then
                # Stop if we hit a non-list line (new top-level key or empty)
                if [[ ! "$line" =~ ^[[:space:]]*- ]]; then
                    break
                fi
                # Extract category name
                category="$(echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*//' | tr -d '[:space:]')"
                [[ -z "$category" ]] && continue

                # Validate it's a known group
                found=false
                for g in "${valid_groups[@]}"; do
                    if [[ "$g" == "$category" ]]; then
                        found=true
                        break
                    fi
                done
                if ! $found; then
                    echo "WARNING: Unknown category '${category}' in ${config}" >&2
                    continue
                fi

                mkdir -p "plugins/${category}/skills"
                # Skip self-referential symlinks (skill already lives in this group dir)
                if [[ "$category" != "$plugin" ]] && [[ ! -L "plugins/${category}/skills/${skill}" ]]; then
                    ln -s "../../${plugin}/skills/${skill}" "plugins/${category}/skills/${skill}"
                fi
            fi
        done < "$config"
    done

    # Report
    echo "sync-groups complete:"
    for group in $(printf '%s\n' "${valid_groups[@]}" | sort); do
        if [[ -d "plugins/${group}/skills" ]]; then
            # Count both symlinks and real skill directories
            count=0
            for entry in "plugins/${group}/skills"/*/; do
                [[ -d "$entry" || -L "${entry%/}" ]] && count=$((count + 1))
            done
            echo "  ${group}: ${count} skills"
        fi
    done

# Generate marketplace.json from all plugin dirs (individual + group)
sync-marketplace:
    #!/usr/bin/env bash
    set -euo pipefail

    declare -A group_descriptions=(
        [all]="All skills — the complete collection"
        [k8s-core]="Kubernetes core infrastructure — helm, kustomize, argocd, k3s, talos, calico, cert-manager, traefik, kubectx"
        [k8s-storage]="Kubernetes storage — rook-ceph, cloudnative-pg"
        [k8s-apps]="Kubernetes applications — authentik, cloudflare, nextcloud, grafana, opentelemetry, openwebui, and more"
        [homelab]="Homelab infrastructure — nixos, vsphere, k3s, talos, pikvm, and more"
        [devops]="DevOps tooling — docker, github, gitlab-ci, goss, and more"
        [frontend]="Frontend development — react, zustand, ui-styling, playwright, svg-logo-designer"
        [golang]="Go development — golang-viper, go-dota2-steam, wails"
        [docs]="Documentation — mkdocs, mermaidjs, zensical, documentation-reviewer"
        [claude-tooling]="Claude Code tooling — claude-code, context-engineering, mcp-management, skill-creator"
        [shell]="Shell tooling — zinit-zsh, zsh-completions"
        [discord]="Discord bot development"
    )

    GROUPS_CSV="all,k8s-core,k8s-storage,k8s-apps,homelab,devops,frontend,golang,docs,claude-tooling,shell,discord"

    entries_file="$(mktemp)"
    trap 'rm -f "$entries_file"' EXIT

    # Emit individual plugin entries (dirs that contain a real config.yaml, not via symlink)
    for plugin_dir in plugins/*/; do
        [[ -d "$plugin_dir" ]] || continue
        plugin="$(basename "$plugin_dir")"

        # Check if this dir has a real (non-symlinked) skill directory with config.yaml
        has_config=false
        for skill_dir in "${plugin_dir}skills"/*/; do
            [[ -d "$skill_dir" ]] || continue
            # Skip symlinked skill directories (those belong to groups)
            [[ -L "${skill_dir%/}" ]] && continue
            [[ -f "${skill_dir}config.yaml" ]] && has_config=true && break
        done
        $has_config || continue

        # Individual plugin — read description from SKILL.md frontmatter
        description=""
        for skill_md in "${plugin_dir}skills"/*/SKILL.md; do
            [[ -f "$skill_md" ]] || continue
            description="$(python3 scripts/extract-description.py "$skill_md")"
            break
        done

        if [[ -z "$description" ]]; then
            description="${plugin} skill for Claude Code"
        fi

        # Truncate to 120 chars
        if [[ ${#description} -gt 120 ]]; then
            description="${description:0:117}..."
        fi

        python3 scripts/json-entry.py "$plugin" "$description" "individual" >> "$entries_file"
    done

    # Emit group plugin entries
    for group in "${!group_descriptions[@]}"; do
        if [[ -d "plugins/${group}/skills" ]]; then
            description="${group_descriptions[$group]}"
            python3 scripts/json-entry.py "$group" "$description" "group" >> "$entries_file"
        fi
    done

    # Assemble the final marketplace.json
    python3 scripts/merge-marketplace.py "$entries_file" "$GROUPS_CSV" \
        > .claude-plugin/marketplace.json

    plugin_count="$(python3 -c "import json; print(len(json.load(open('.claude-plugin/marketplace.json'))['plugins']))")"
    echo "sync-marketplace complete: ${plugin_count} plugins written"
