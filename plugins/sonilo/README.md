# Sonilo

Generate commercially licensed music, sound effects, newly mixed videos,
translated subtitles, and dubbed videos from text, a video URL, or a local
file — powered by Sonilo's hosted generation service.

## What it ships

- **MCP server** `sonilo_platform` — the hosted Sonilo MCP at
  `https://api.sonilo.com/mcp` (Streamable HTTP).
- **Skill** `sonilo-workflows` — how to pick the right tool, upload a local
  file, poll a task, and report balances and results accurately.

No hooks, commands, agents, scripts, or local binaries.

## Network endpoints

| Endpoint | Why |
| --- | --- |
| `https://api.sonilo.com/mcp` | The MCP server: every tool call |
| `https://clerk.platform.sonilo.com` | OAuth 2.1 + PKCE sign-in (dynamic client registration) |
| The presigned `upload_url` returned by `create_upload_url` | Uploading a local file the user asked to process, with `curl -T` |

## Credentials

A Sonilo Platform account, signed in through the browser on first connect.
Grok Build stores the OAuth token; the plugin ships no key, secret, or token
and reads no environment variables or local credentials.

See the [repository README](https://github.com/sonilo-ai/sonilo-grok-plugin)
for installation, capabilities, and billing.
