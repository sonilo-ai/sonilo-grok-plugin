# Subtitle review, previews, and full videos

## Review the script before dubbing

1. For “translate the subtitles first; I will correct them,” use
   `generate_video_subtitles` only. It may consume credits; it produces SRT
   files, not a dubbed video. Check that the `proofread` service is available
   before submitting; its trial runs are listed under `proofread` too.
2. Return the source transcript and target-language SRT URLs actually present
   in the result. Report warnings without claiming the files are invalid
   unless the service says so. Wait for the user's review before dubbing.
3. Use the approved target-language scripts as `dubbing.subtitles`, one
   HTTPS SRT/VTT URL per target language, with keys matching the requested
   languages exactly. Validate every subtitle URL as well as the video URL.
   If the user edits the text, in chat or in a local file, do not silently
   reuse the unedited SRT: save the approved script as a local `.srt` that
   keeps the original cue timings, upload it with `create_upload_url`, and
   pass its `file_url`.
4. Set `export_srt=true` only if the user wants aligned subtitles with the
   dubbed result and scripts were supplied. Deliver each language's video
   and any successful subtitle export; report a blocked export separately.

## Select languages and preview eligibility

- Always specify the languages the user requested; never omit this argument
  and accidentally accept the server's multiple-language default. Ask for the
  target language if missing. Dubbing is billed per language.
- Follow the hosted schema: `dubbing.languages` currently takes a JSON array
  encoded as a string (for example, `["en"]`), while
  `generate_video_subtitles.languages` takes a list. Do not copy local MCP
  parameter types or its `video_path` options; local files go through
  `create_upload_url`.
- A free dubbing preview is conditional on current account eligibility, a
  single target language, and no supplied subtitles. Check
  `trial.dubbing.remaining`; never promise every user a free preview.
- The eligible first call processes up to the first 15 seconds. A free-only
  request does not authorize a normal charged call when eligibility is absent,
  exhausted, unknown, or incompatible with multiple languages or scripts.
  Explain that no free preview is available; do not silently bill instead.
- Read `trial_preview` from both submission text and the retrieved task result.
  Use `preview_seconds`, `source_duration_seconds`, and `trimmed` to label the
  actual preview. Do not say 45 seconds remain unless the source is 60 seconds.
- `full_video_cost_usd`, when present, describes the full source, not the
  amount charged for the preview. Do not infer the current balance from it.

## Continue after a preview or account update

- A preview is complete for that preview task. Polling it again cannot make
  it full length. Never automatically submit a second dubbed video.
- When the user explicitly asks for the full version, reuse the original
  video URL (for an uploaded file, the same `file_url`), target language, and
  approved settings. Refresh account services;
  the full source is a new generation and may use existing paid credits.
  Do not promise it charges only for the remaining seconds.
- If a previous full-video task exists, retrieve it instead of starting a
  duplicate. If only the completed preview exists, the explicit full-video
  request authorizes one new submission. Stop on a credit rejection.
- If the first request was for a full video but the server returns a preview,
  deliver it accurately and explain how to request the full version with
  existing access. Do not automatically make another charged call.
- If the user later says their account is updated and asks to continue, apply
  the same task check and refresh. Report the actual USD balance when returned;
  do not promise it covers the full video. If the connected response lacks a
  balance, say so and let the service enforce billing on the requested task.
- Use `lipsync=false` only when requested or needed to preserve the original
  picture; use `ducking=true` when the background must lower under the dubbed
  speech. Follow current defaults otherwise.
