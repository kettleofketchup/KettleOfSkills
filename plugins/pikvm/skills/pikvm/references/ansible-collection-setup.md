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
├── galaxy.yml                       # Collection metadata (required)
├── README.md                        # Collection readme (required, .md only)
├── meta/
│   └── runtime.yml                  # Version requirements, plugin routing
├── plugins/
│   ├── modules/                     # Module plugins (flat, no subdirs)
│   │   ├── pikvm_msd.py
│   │   ├── pikvm_atx.py
│   │   ├── pikvm_hid.py
│   │   └── pikvm_info.py
│   ├── module_utils/                # Shared Python code
│   │   ├── __init__.py
│   │   ├── pikvm_client.py          # HTTP client (uses open_url)
│   │   └── pikvm_common.py          # Shared argument_spec, doc fragment ref
│   └── doc_fragments/               # Shared documentation fragments
│       └── pikvm_auth.py
├── tests/
│   ├── unit/
│   │   └── plugins/
│   │       ├── modules/
│   │       │   └── test_pikvm_msd.py
│   │       └── module_utils/
│   │           └── test_pikvm_client.py
│   ├── integration/
│   │   ├── integration_config.yml   # Test vars (pikvm_host, credentials)
│   │   └── targets/
│   │       ├── pikvm_msd/
│   │       │   ├── tasks/main.yml
│   │       │   └── aliases          # e.g. "destructive\nneeds/target/setup_pikvm"
│   │       └── pikvm_info/
│   │           ├── tasks/main.yml
│   │           └── aliases
│   └── sanity/
│       └── ignore-2.17.txt          # Sanity test exceptions
├── changelogs/
└── .ansible-lint
```

Constraints: roles cannot contain plugins. Filter/test plugin dirs use singular names (`filter/`, `test/`).

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

```yaml
name: Collection Tests
on: [push, pull_request]
jobs:
  sanity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: ansible_collections/mynamespace/pikvm
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ansible-core
      - run: ansible-test sanity --local --python 3.11
        working-directory: ansible_collections/mynamespace/pikvm

  units:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: ansible_collections/mynamespace/pikvm
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ansible-core pytest
      - run: ansible-test units --local --python 3.11
        working-directory: ansible_collections/mynamespace/pikvm
```
