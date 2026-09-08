"""Tests for the pure (network-free) parts of vault_probe.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import vault_probe as vp  # noqa: E402


class TestNormalizeBase:
    def test_appends_api_suffix(self):
        assert vp.normalize_base("http://vault.local") == (
            "http://vault.local/AutodeskDM/Services/api/vault/v2"
        )

    def test_strips_trailing_slash(self):
        assert vp.normalize_base("http://vault.local/") == (
            "http://vault.local/AutodeskDM/Services/api/vault/v2"
        )

    def test_idempotent_when_suffix_present(self):
        url = "http://vault.local/AutodeskDM/Services/api/vault/v2"
        assert vp.normalize_base(url) == url

    def test_trims_past_the_suffix(self):
        url = "http://vault.local/AutodeskDM/Services/api/vault/v2/users/9"
        assert vp.normalize_base(url) == (
            "http://vault.local/AutodeskDM/Services/api/vault/v2"
        )

    def test_bare_host_defaults_to_http(self):
        assert vp.normalize_base("vault.local").startswith("http://vault.local")

    def test_bare_gateway_host_defaults_to_https(self):
        assert vp.normalize_base("abc.vg.autodesk.com").startswith("https://")

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            vp.normalize_base("   ")


class TestIsGateway:
    def test_gateway_detected(self):
        assert vp.is_gateway("https://abc123.vg.autodesk.com/AutodeskDM") is True

    def test_direct_server_not_gateway(self):
        assert vp.is_gateway("http://vault.local/AutodeskDM") is False


SPEC = """\
openapi: 3.0.1
info:
  title: Vault Data API
paths:
  /server-info:
    get:
      summary: server info
  /sessions:
    post: {}
  /vaults/{vaultId}/files/{id}/versions:
    get: {}
  /vaults/{vaultId}/folders/{id}/contents:
    get: {}
  /users/{id}:
    get: {}
components:
  schemas:
    /not-a-path:
      type: object
"""


class TestParseOpenapiPaths:
    def test_extracts_routes(self):
        paths = vp.parse_openapi_paths(SPEC)
        assert "/server-info" in paths
        assert "/sessions" in paths
        assert "/vaults/{vaultId}/files/{id}/versions" in paths
        assert len(paths) == 5

    def test_stops_at_next_top_level_key(self):
        assert "/not-a-path" not in vp.parse_openapi_paths(SPEC)

    def test_no_paths_block(self):
        assert vp.parse_openapi_paths("openapi: 3.0.1\ninfo:\n  title: x\n") == []

    def test_empty_input(self):
        assert vp.parse_openapi_paths("") == []


class TestGroupEndpoints:
    def test_groups_by_family(self):
        groups = vp.group_endpoints(vp.parse_openapi_paths(SPEC))
        assert set(groups) == {"server-info", "sessions", "files", "folders", "users"}

    def test_vault_scoped_routes_use_second_segment(self):
        groups = vp.group_endpoints(["/vaults/{vaultId}/items/{id}"])
        assert "items" in groups

    def test_bare_vaults_route_stays_vaults(self):
        assert "vaults" in vp.group_endpoints(["/vaults"])


class TestVersionCapabilities:
    def test_2025_2_has_read_api_only(self):
        caps = dict(vp.version_capabilities("2025.2"))
        assert caps["Vault Data API (read: files, folders, items, BOM, search, users)"] is True
        assert caps["Lifecycle definition/state read and update over REST"] is False

    def test_2027_1_has_lifecycle_writes(self):
        caps = dict(vp.version_capabilities("2027.1"))
        assert all(v is True for v in caps.values())

    def test_2024_below_every_gate(self):
        caps = dict(vp.version_capabilities("2024"))
        assert all(v is False for v in caps.values())

    def test_unparseable_version_is_unknown(self):
        assert all(v is None for _, v in vp.version_capabilities("Vault Professional"))

    def test_missing_version_is_unknown(self):
        assert all(v is None for _, v in vp.version_capabilities(None))

    def test_version_embedded_in_product_string(self):
        caps = dict(vp.version_capabilities("Autodesk Vault Professional 2026.1"))
        assert caps["Vault Data API (read: files, folders, items, BOM, search, users)"] is True


class TestRender:
    def _report(self, **over):
        base = {
            "base_url": "http://v/AutodeskDM/Services/api/vault/v2",
            "gateway": False,
            "server_info_status": 200,
            "server_info": {"version": "2026.0"},
            "capabilities": [{"capability": "X", "available": True}],
            "openapi_status": 200,
            "endpoints": {"files": ["/vaults/{v}/files/{id}"]},
        }
        base.update(over)
        return base

    def test_renders_reachable_server(self):
        out = vp.render(self._report())
        assert "direct server" in out
        assert "[    yes] X" in out
        assert "files (1)" in out

    def test_renders_unreachable_server(self):
        out = vp.render(
            self._report(server_info_status=0, server_info=None, server_info_error="refused")
        )
        assert "UNREACHABLE" in out

    def test_gateway_openapi_note_shown(self):
        out = vp.render(
            self._report(
                gateway=True, openapi_status=404, endpoints=None, openapi_note="gateway 404 note"
            )
        )
        assert "Vault Gateway" in out
        assert "gateway 404 note" in out


class TestMain:
    def test_errors_without_server(self, monkeypatch, capsys):
        monkeypatch.delenv("VAULT_SERVER_URL", raising=False)
        with pytest.raises(SystemExit):
            vp.main([])
        assert "no server given" in capsys.readouterr().err
