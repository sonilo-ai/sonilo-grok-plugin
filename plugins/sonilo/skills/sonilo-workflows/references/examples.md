# User-facing examples

Respond in the user's language. Link labels mean real user inputs or returned
artifacts, not invented URLs. Use success wording only after a successful
result; substitute actual account data for illustrative numbers.

| User request | Behavior and response shape |
| --- | --- |
| “Translate this one-minute product demo into English subtitles first; I will correct the product name.” + video URL | Run `generate_video_subtitles`, return the English SRT link, and wait: “Review this English subtitle file. Send the corrected script, or tell me the changes, when you are ready to dub.” |
| “Add upbeat music to `./cuts/launch.mp4` and give me the finished video.” | Read the file's size, call `create_upload_url`, PUT the file with `curl -T`, then run `video_to_video_music` once with the returned `file_url`. “Here is your new video with music: [video].” Do not show the upload URL; download the result only if asked. |
| “Add relaxed music and waves to this 20-second beach video and give me the finished video.” + video URL | Run `video_to_video_sound` once. “Here is your new video with music and wave effects: [video].” |
| “Let me try English dubbing for free on this one-minute Chinese video.” + video URL | Check single-language, no-script trial eligibility. If confirmed and the task succeeds with a trimmed preview: “Here is the first 15 seconds in English: [preview]. The remaining 45 seconds have not been processed.” Otherwise explain that a free preview is unavailable without submitting a paid job. |
| “That preview sounds good. Dub the whole one-minute video.” | Refresh services, check for an existing full-video task, then submit once using the original source and English settings. “I will check your account and use the same video and language for the full version.” Do not claim it is already complete. |
| “How much balance do I have, and how many free music runs remain?” | Call `get_account_services`. If it returns `cash_balance="2.5001"`, `currency="USD"`, and `trial.text_to_music.remaining=1`: “Your current cash balance is USD 2.5001. You have 1 free text-to-music run remaining.” Use actual returned values. If balance is missing: “The service did not return your cash balance.” Missing trial data is unknown, not zero. |
| “Generate another 30-second upbeat track.” when rejected for insufficient balance | “The service reports insufficient balance.” If a fresh account lookup returns `cash_balance="0.0000"` and `currency="USD"`, add “Your current cash balance is USD 0.” Add “Generation did not start” only for a confirmed pre-generation rejection. Add “[Balance and free trials](https://platform.sonilo.com/usage-and-entitlements) explains how balance and trial limits work.” No automatic retry. |
| “My account credits have updated. Continue the English video from before.” | Refresh account data and retrieve any prior task. Submit once only after a confirmed rejection or when the only completed task is a preview and the user wants the full video. If the refreshed response returns `cash_balance="5.0000"` and `currency="USD"`: “Your current cash balance is USD 5. I will use the same video and English settings; the service checks available funds when processing the request.” A positive balance alone does not prove sufficient funds. |
| “I am new to Sonilo. How do I ask for music for a café ad?” | No generation. “Give me the video's path or a public HTTPS link and say: ‘Add warm, relaxed jazz to this 30-second café ad.’” For more examples, link to `https://platform.sonilo.com/mcp`. |
| “Is the English video ready?” | Retrieve the same task ID. While processing: “It is still processing. I am checking the original task, not submitting another generation.” If waiting stops, provide the task ID without promising unattended monitoring. |
| “Give me three music choices for this 30-second café ad.” + video URL | Use `video_to_music` with `variants_num=3`, or the video-output tool if requested. Multiple variants use paid credits; a free-only constraint prevents this submission. Return three separately labeled actual URLs after success. |
| “Add light music to my travel narration, but keep my voice clear.” + video URL | Use the requested output type with `preserve_speech=true` and `ducking=true` where supported. Link to the actual processed output, not an unducked alternative. |
| “At 2–3 seconds add a door closing; at 5–7 seconds add rain.” + video URL | Use the requested SFX output type. For the hosted contiguous-segment schema, encode 0–2 no added effects, 2–3 door closing, 3–5 no added effects, and 5–7 rain. Return the actual audio or video after success. |
| “Generate 30 seconds of jazz and give me separate drums and bass for editing.” | `text_to_music` with `duration=30`, `stems=true`. Return [complete music], [drums], [bass], and other actual stem URLs. A stems-only failure does not invalidate the complete music. |

## Concrete credit-error replies

These examples assume the server confirmed rejection before task creation and
that the fresh account lookup returned the stated balance. Omit unconfirmed
facts. A trial count is included only if returned for that specific service.

**User:** “再帮我生成一段 30 秒的轻快背景音乐。”

**Reply:** “余额不足，这次没有开始生成。你当前的余额是 USD 0。
可查看[余额与免费试用](https://platform.sonilo.com/zh/usage-and-entitlements)了解规则。
账户更新后，可以对我说‘继续刚才的音乐’。”

**User:** “再免費試一次英文配音。”

**Reply when the dubbing trial is confirmed exhausted:** “你的英文配音免費試用
次數已用完，這次沒有開始生成。可查看
[餘額與免費試用](https://platform.sonilo.com/zh-HK/usage-and-entitlements)了解規則。”

A zero remaining trial count alone does not prove insufficient paid balance.
For a free-only request, do not submit a paid job to test whether it will work.
If account lookup fails after a credit rejection, report the original rejection
and say the current balance could not be retrieved; retain the guide link.
