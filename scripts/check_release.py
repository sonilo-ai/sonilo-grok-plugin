#!/usr/bin/env python3
"""Validate the Sonilo Grok plugin package and optional production surfaces."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "sonilo"
MANIFEST_PATH = PLUGIN_ROOT / ".grok-plugin" / "plugin.json"
MCP_PATH = PLUGIN_ROOT / ".mcp.json"
PLUGIN_README_PATH = PLUGIN_ROOT / "README.md"
WORKFLOW_SKILL_PATH = PLUGIN_ROOT / "skills" / "sonilo-workflows" / "SKILL.md"
MARKETPLACE_PATH = ROOT / ".grok-plugin" / "marketplace.json"
MCP_URL = "https://api.sonilo.com/mcp"
RESOURCE_METADATA_URL = f"{MCP_URL}/.well-known/oauth-protected-resource"
RFC_RESOURCE_METADATA_URL = "https://api.sonilo.com/.well-known/oauth-protected-resource/mcp"
AUTHORIZATION_SERVER = "https://clerk.platform.sonilo.com/"
BALANCE_GUIDE_PATH = WORKFLOW_SKILL_PATH.parent / "references" / "account-and-links.md"
BALANCE_GUIDE_URLS = {
    f"https://platform.sonilo.com{prefix}/usage-and-entitlements"
    for prefix in ("", "/zh", "/zh-HK", "/de", "/es", "/fr", "/it", "/ja", "/ko", "/pt")
}
HOSTED_TOOL_NAMES = {
    "text_to_music",
    "text_to_sfx",
    "video_to_music",
    "video_to_sfx",
    "video_to_video_music",
    "video_to_video_sfx",
    "audio_ducking",
    "video_to_sound",
    "video_to_video_sound",
    "generate_video_subtitles",
    "dubbing",
    "analyze_video",
    "create_upload_url",
    "get_account_services",
    "get_usage",
    "get_generation_task",
}
# The xAI catalog rejects generic keywords: they drive the plugin suggestion
# prompt, so every term has to be scoped to the brand.
BRAND_TERM = "sonilo"
OWNED_DOMAINS = {"sonilo.com", "platform.sonilo.com", "api.sonilo.com"}


class CheckFailure(RuntimeError):
    """Raised when a release invariant is not satisfied."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckFailure(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def check_local() -> None:
    manifest = load_json(MANIFEST_PATH)
    mcp_config = load_json(MCP_PATH)
    marketplace = load_json(MARKETPLACE_PATH)

    require(manifest.get("name") == "sonilo", "manifest name must be sonilo")
    require(
        re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")) is not None,
        "manifest version must be a plain semver string",
    )
    require(bool(manifest.get("description", "").strip()), "manifest description is missing")
    require(manifest.get("license") == "MIT", "manifest must state the MIT license")
    require((ROOT / "LICENSE").is_file(), "LICENSE file is missing")
    require(PLUGIN_README_PATH.is_file(), "plugin README is missing")
    require(WORKFLOW_SKILL_PATH.is_file(), "bundled sonilo-workflows skill is missing")

    servers = mcp_config.get("mcpServers", {})
    require(set(servers) == {"sonilo_platform"}, "hosted MCP must avoid the legacy local sonilo server name")
    sonilo_mcp = servers["sonilo_platform"]
    require(sonilo_mcp.get("type") == "http", "MCP transport type must be http")
    require(sonilo_mcp.get("url") == MCP_URL, f"MCP URL must be {MCP_URL}")
    require(
        set(sonilo_mcp) == {"type", "url"},
        "MCP config must contain only the endpoint: no headers, command, or credentials",
    )

    author = manifest.get("author", {})
    require(author.get("name") == "Sonilo", "public author name must be Sonilo")
    require(author.get("email") == "support@sonilo.com", "support email is missing")
    require(author.get("url") == "https://platform.sonilo.com", "author URL must use Sonilo Platform")
    require(manifest.get("homepage") == "https://platform.sonilo.com", "homepage must use Sonilo Platform")

    logo = manifest.get("logo")
    require(isinstance(logo, str) and bool(logo), "manifest logo is missing")
    logo_path = (PLUGIN_ROOT / logo).resolve()
    require(logo_path.is_relative_to(PLUGIN_ROOT.resolve()), "logo must live inside the plugin")
    require(logo_path.is_file(), f"missing logo: {logo}")

    # The plugin is a remote MCP server plus a skill. Anything executable would
    # change what the catalog's security review has to cover.
    for component in ("hooks", "commands", "agents", "scripts", ".lsp.json"):
        require(not (PLUGIN_ROOT / component).exists(), f"plugin must not ship {component}")

    skill = WORKFLOW_SKILL_PATH.read_text(encoding="utf-8")
    require(skill.startswith("---\nname: sonilo-workflows\n"), "skill frontmatter is invalid")
    # References ship with the skill and are loaded only for the relevant workflow.
    # Validate actual links so a missing packaged reference cannot silently drop
    # account or dubbing guidance from the installed plugin.
    references = re.findall(r"\]\((references/[^)]+\.md)\)", skill)
    require(bool(references), "skill must link its workflow references")
    for relative_path in set(references):
        reference = WORKFLOW_SKILL_PATH.parent / relative_path
        require(reference.is_file(), f"missing bundled reference: {relative_path}")
    guidance = skill + "\n" + "\n".join(
        (WORKFLOW_SKILL_PATH.parent / path).read_text(encoding="utf-8")
        for path in sorted(set(references))
    )
    require("only when the user clearly asks" in skill, "skill must guard paid operations")
    for tool_name in HOSTED_TOOL_NAMES:
        require(f"`{tool_name}`" in skill, f"skill is missing guidance for {tool_name}")
    # `proofread` survives only as the service and trial key of the subtitle
    # tool; tools/list no longer advertises it as a tool.
    require("use `proofread`" not in guidance, "guidance still routes to the unlisted proofread tool")
    require("Run `proofread`" not in guidance, "guidance still routes to the unlisted proofread tool")
    require(
        "new video with the generated audio mixed in" in skill,
        "skill must distinguish video-producing tools from audio-only tools",
    )
    require("`preserve_speech=true`" in skill, "skill must document speech preservation routing")
    require("isolate_vocals" not in guidance, "obsolete local-only parameter in hosted guidance")
    require("A Sonilo Platform account is required" in skill, "skill must state the required account system")
    require(
        "Accounts created only on `sonilo.com`" in skill,
        "skill must disclose that sonilo.com accounts are separate",
    )
    require(
        "Never direct users to `sonilo.com` for plugin authentication" in skill,
        "skill must not route authentication to the wrong account system",
    )
    require(
        "Require a publicly reachable `https://` URL" in skill,
        "skill must validate user-supplied media URLs",
    )
    require(
        "Never upload it to any other host" in skill,
        "skill must confine local-file uploads to the returned upload URL",
    )
    require(
        "do not show it to the user" in skill,
        "skill must keep the presigned upload URL out of the reply",
    )
    require("curl -sS -f -T" in skill, "skill must document the upload PUT")
    guide_reference = BALANCE_GUIDE_PATH.read_text(encoding="utf-8")
    guide_urls = set(re.findall(
        r"https://platform\.sonilo\.com[^\s|)]*/usage-and-entitlements[^\s|)]*",
        guide_reference,
    ))
    require(
        guide_urls == BALANCE_GUIDE_URLS,
        "balance guide must configure all 10 published routes without query data or invented paths",
    )
    require("Poll `get_generation_task`" in skill, "skill must document asynchronous polling")

    entries = marketplace.get("plugins", [])
    entry = next((item for item in entries if item.get("name") == "sonilo"), None)
    require(entry is not None, "marketplace is missing the sonilo entry")
    require(entry.get("source") == "./plugins/sonilo", "marketplace source path is wrong")
    require(entry.get("homepage") == manifest["homepage"], "marketplace homepage is out of sync")
    require(entry.get("keywords") == manifest.get("keywords"), "marketplace keywords are out of sync")
    keywords = entry.get("keywords") or []
    require(bool(keywords), "marketplace keywords are missing")
    require(
        all(BRAND_TERM in keyword for keyword in keywords),
        "every keyword must be brand-scoped",
    )
    require(set(entry.get("domains", [])) == OWNED_DOMAINS, "domains must be exactly the ones Sonilo owns")


def request(url: str, *, method: str = "GET") -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={"Accept": "application/json", "User-Agent": "sonilo-plugin-release-check/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            headers = {name.lower(): value for name, value in response.headers.items()}
            return response.status, headers, response.read()
    except urllib.error.HTTPError as exc:
        headers = {name.lower(): value for name, value in exc.headers.items()}
        return exc.code, headers, exc.read()
    except urllib.error.URLError as exc:
        raise CheckFailure(f"could not reach {url}: {exc.reason}") from exc


def check_live() -> None:
    status, headers, _ = request(MCP_URL)
    require(status == 401, f"unauthenticated MCP request returned {status}, expected 401")
    challenge = headers.get("www-authenticate", "")
    require("Bearer" in challenge, "MCP response is missing the Bearer challenge")
    require(RESOURCE_METADATA_URL in challenge, "MCP challenge points at the wrong resource metadata URL")

    def validate_resource_metadata(metadata_url: str, body: bytes) -> None:
        try:
            metadata = json.loads(body)
        except json.JSONDecodeError as exc:
            raise CheckFailure(f"resource metadata at {metadata_url} is not valid JSON") from exc
        require(metadata.get("resource") == MCP_URL, "resource metadata contains the wrong resource")
        require(AUTHORIZATION_SERVER in metadata.get("authorization_servers", []), "authorization server is missing")
        require("profile" in metadata.get("scopes_supported", []), "profile scope is missing")
        require("header" in metadata.get("bearer_methods_supported", []), "header bearer method is missing")

    status, _, body = request(RESOURCE_METADATA_URL)
    require(status == 200, f"resource metadata at {RESOURCE_METADATA_URL} returned {status}, expected 200")
    validate_resource_metadata(RESOURCE_METADATA_URL, body)

    status, _, body = request(RFC_RESOURCE_METADATA_URL)
    require(
        status == 200,
        f"RFC discovery fallback at {RFC_RESOURCE_METADATA_URL} returned {status}, expected 200",
    )
    validate_resource_metadata(RFC_RESOURCE_METADATA_URL, body)

    manifest = load_json(MANIFEST_PATH)
    status, _, _ = request(manifest["homepage"])
    require(status == 200, f"homepage returned {status}, expected 200")

    for url in sorted(BALANCE_GUIDE_URLS):
        status, headers, body = request(url)
        require(status == 200, f"balance guide {url} returned {status}, expected 200")
        require("text/html" in headers.get("content-type", ""), f"guide is not HTML: {url}")
        html = body.decode("utf-8")
        canonical = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', html)
        require(canonical is not None and canonical[1] == url, f"wrong guide canonical: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="also check production HTTP and OAuth metadata")
    args = parser.parse_args()

    try:
        check_local()
        if args.live:
            check_live()
    except CheckFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    scope = "local and live" if args.live else "local"
    print(f"PASS: Sonilo release checks ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
