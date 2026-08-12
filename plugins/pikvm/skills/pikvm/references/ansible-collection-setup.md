# Ansible Collection Setup & Tooling

## ansible-creator Scaffolding

```bash
pip install ansible-dev-tools  # installs ansible-creator, ansible-lint, molecule, ansible-test

# Scaffold collection
ansible-creator init collection mynamespace.pikvm ~/collections/ansible_collections

# Add module to existing collection
ansible-creator add plugin module pikvm_msd /path/to/mynamespace/pikvm

# Install collection in editable mode for dev
pip install ansible-dev-environment && ade install -e .
```

Supported plugin types: `action`, `filter`, `lookup`, `module`, `test`
Supported resource types: `devcontainer`, `devfile`, `execution-environment`, `play-argspec`, `role`

## Collection Directory Structure

```
mynamespace/pikvm/
├── galaxy.yml            # Collection metadata
├── meta/runtime.yml      # Ansible version requirements
├── plugins/
│   ├── modules/          # Flat dir: pikvm_msd.py, pikvm_atx.py, pikvm_hid.py, pikvm_info.py
│   ├── module_utils/     # pikvm_client.py (open_url), pikvm_common.py
│   └── doc_fragments/    # pikvm_auth.py
├── tests/
│   ├── unit/             # tests/unit/plugins/modules/test_pikvm_msd.py
│   ├── integration/      # targets/{pikvm_msd,pikvm_info}/{tasks/main.yml,aliases}
│   └── sanity/ignore-2.17.txt
└── .ansible-lint
```

Constraints: roles cannot contain plugins. Filter/test dirs use singular names (`filter/`, `test/`).

## galaxy.yml

```yaml
namespace: mynamespace
name: pikvm
version: 1.0.0
readme: README.md
authors:
  - "Your Name <you@example.com>"
description: Manage PiKVM devices via HTTP API
license:
  - GPL-3.0-or-later
tags: [kvm, pikvm, remote_management, infrastructure]
dependencies: {}
repository: https://github.com/you/ansible-collection-pikvm
build_ignore:
  - "*.tar.gz"
  - .github
  - tests/integration/integration_config.yml
```

## meta/runtime.yml

```yaml
requires_ansible: ">=2.15.0"
plugin_routing:
  modules: {}
```

## Testing with ansible-test

**IMPORTANT:** ansible-test requires collection at `ansible_collections/{namespace}/{name}/` relative to working directory.

### Sanity Tests

```bash
ansible-test sanity --docker                              # all tests
ansible-test sanity plugins/modules/pikvm_msd.py --docker # specific file
ansible-test sanity --test validate-modules --docker      # specific test
ansible-test sanity --local --python 3.11                 # local execution
```

Key sanity tests: `validate-modules` (docs/argspec), `import`, `pep8`, `pylint`, `yamllint`, `compile`

### Unit Tests

```bash
ansible-test units --docker
ansible-test units tests/unit/plugins/modules/test_pikvm_msd.py --docker
```

### Integration Tests

```bash
ansible-test integration --docker
ansible-test integration pikvm_msd --docker -vvv
```

Integration config (`tests/integration/integration_config.yml`):
```yaml
pikvm_host: 10.0.0.100
pikvm_user: admin
pikvm_passwd: admin
pikvm_verify_ssl: false
```

## ansible-lint Configuration

`.ansible-lint`:
```yaml
profile: production
skip_list:
  - fqcn[action-core]
  - yaml[line-length]
warn_list:
  - no-changed-when
exclude_paths:
  - tests/integration/
```

Key rules: `fqcn` (use FQCN), `name` (descriptive task names), `no-changed-when`, `risky-file-permissions`, `no-log-password`, `schema`, `galaxy`, `meta-runtime`

Profiles (least to most strict): min → basic → moderate → safety → shared → production

## CI/CD: GitHub Actions

Checkout to `ansible_collections/mynamespace/pikvm`, install `ansible-core`, run ansible-test from that directory:

```yaml
- uses: actions/checkout@v4
  with: { path: ansible_collections/mynamespace/pikvm }
- uses: actions/setup-python@v5
  with: { python-version: "3.11" }
- run: pip install ansible-core
- run: ansible-test sanity --local --python 3.11
  working-directory: ansible_collections/mynamespace/pikvm
```

Add a second job replacing `sanity` with `units --local --python 3.11` (also install `pytest`).
