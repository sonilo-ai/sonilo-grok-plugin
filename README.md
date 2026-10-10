# Sonilo for Grok

Generate commercially licensed music, sound effects, newly mixed videos,
translated subtitles, and dubbed videos from text, a video URL, or a local
file, directly in Grok Build — powered by Sonilo's hosted generation service.

> Status: not yet published. This plugin is not listed in the
> [xAI plugin marketplace](https://github.com/xai-org/plugin-marketplace) yet;
> install it from this repository.

## Requirements

- A **Sonilo Platform** account at
  [platform.sonilo.com](https://platform.sonilo.com/sign-up) — this is the
  developer/API account you sign in with during authorization. It is separate
  from a consumer `sonilo.com` account; if you only have the latter, create a
  Platform account first.
- [Grok Build](https://docs.x.ai/build/overview).

No API key is configured in this plugin. Access is per-user via OAuth — you
sign in with your Sonilo Platform account, no key to copy or paste.

## Install

```bash
grok plugin install 'sonilo-ai/sonilo-grok-plugin#plugins/sonilo' --trust
```

### Local development installation

```bash
git clone https://github.com/sonilo-ai/sonilo-grok-plugin.git
grok plugin install "$PWD/sonilo-grok-plugin#plugins/sonilo" --trust
```

`grok plugin validate ./sonilo-grok-plugin/plugins/sonilo` checks the manifest,
and `grok inspect` shows the loaded skill and MCP server.

## Authorize

The first time Grok calls a Sonilo tool, it opens your browser to sign in to
your [Sonilo Platform](https://platform.sonilo.com) account and approve access.
Grok stores the resulting token locally per user; the plugin itself ships no
key, secret, or token. Open `/mcps` and authenticate `sonilo_platform` anytime
to review or refresh the connection; `grok mcp doctor sonilo_platform`
diagnoses it.

The bundled connection is named `sonilo_platform` so an existing local Python
MCP named `sonilo` cannot override it.

## Capabilities

- Create music from a text prompt
- Match music to the pacing and edits of a video
- Generate sound effects from text or a video
- Return a new video with generated music while optionally preserving speech
- Return a new video with generated sound effects mixed in
- Generate music and sound effects together in one soundtrack or new video
- Generate multiple music versions and separate instrument stems
- Place sound effects at specified times
- Duck music under voice audio
- Review translated subtitles before dubbing into the requested languages
- Use an eligible account's 15-second dubbing preview, then request a full video
- Inspect current USD cash balance, account services, trial allowance, and historical usage
- Retrieve an existing generation after waiting or a timeout without resubmission

Features depend on the connected hosted tool schemas and account access.

### Local files

Sonilo's tools take media as URLs. For a file on your machine, Grok asks the
service for a one-time upload URL (`create_upload_url`), sends the file with
`curl -T`, and passes the resulting link to the tool you asked for. Videos,
audio, and `.srt`/`.vtt` subtitles are accepted, up to your account's upload
limit. Uploads are temporary working files, not storage. Grok uploads only
the file you asked it to process.

### Example prompts

- "Create 30 seconds of upbeat lo-fi music for a product demo."
- "Create a cinematic 3-second whoosh sound effect."
- "Add cinematic music to `./cuts/launch.mp4` and give me a new video, keeping the speech."
- "Give me three music choices for this 30-second café ad: `<video URL>`"
- "Generate 30 seconds of jazz with separate drums and bass tracks."
- "Translate `./ep1.mp4` into English subtitles first. I will correct the product names before dubbing."
- "Let me try English dubbing for free: `<video URL>`"
- "What is my cash balance, and how many free text-to-music runs remain?"

Media URLs must be public HTTPS links. The plugin returns actual result links
for previews, subtitles, videos, variants, and stems.

## Billing

Generation, transcription, dubbing, and video-analysis tools can consume
existing account credits. Available free runs depend on the service and
account; dubbing previews require one target language and no supplied script.
Multiple music variants and multi-language dubbing can cost more. Account,
task, and upload tools (`get_account_services`, `get_usage`,
`get_generation_task`, `create_upload_url`) never incur a charge. Paid tools
run only after you explicitly ask for them.

## What this plugin connects to

This plugin adds a single **remote MCP server** and one skill:

- **Endpoint:** `https://api.sonilo.com/mcp` (HTTPS, Streamable HTTP MCP)
- **Authorization server:** Sonilo's Clerk instance at
  `clerk.platform.sonilo.com` (OAuth 2.1 + PKCE; the client registers
  dynamically — no pre-shared client secret)
- **Uploads:** a local file you ask Grok to process is sent with an HTTP PUT
  to the presigned URL returned by `create_upload_url`
- **Data sent:** your prompts, any media URLs you provide, and any local file
  you ask to have processed
- **Data stored:** the OAuth token, kept locally per user by Grok

The plugin ships no hooks, scripts, or binaries, and reads no environment
variables or local credentials.

## Support

- Platform / account: [platform.sonilo.com](https://platform.sonilo.com)
- Website: [sonilo.com](https://sonilo.com)
- Contact: info@sonilo.com

## Release verification

Run the structural checks locally:

```bash
python3 scripts/check_release.py
```

Include production endpoint, OAuth metadata, and public-link checks:

```bash
python3 scripts/check_release.py --live
```

## License

MIT — see [LICENSE](LICENSE).
