# Account status and links

## Answer balance and trial questions

- `get_account_services` supplies available services and, when present,
  `trial[service].granted`, `used`, and `remaining`. Name the service when
  reporting counts; a music trial does not cover a different endpoint.
- An absent or null `trial` does not mean zero balance or unlimited free use.
  A missing service entry does not establish a free trial. Zero trial runs
  does not establish zero paid balance; existing paid access may still work.
- `get_usage` supplies requests, durations, and spending for its date range.
  `summary.total_cost` is spending, never the remaining cash or credit balance.
- `get_account_services` also returns `cash_balance` as a decimal string and
  `currency` as `USD`. Report the actual amount in US dollars, preserving
  sub-cent precision when present (for example, `"2.5001"` is USD 2.5001).
  Use this read-only tool for balance questions; call `get_usage` only when
  the user also wants spending history. Never subtract usage from an assumed
  deposit or convert dollars into invented credits or generation counts.
- Check that both balance and currency are present and valid. `"0.0000"` is
  a known zero; missing, null, or invalid balance data is unavailable, not zero.
  If an older connected response lacks these fields, report the available
  trial data and explain that the balance was not returned.
- This is the authenticated account's balance at query time, not a reserved
  amount or authorization for another generation. Zero cash does not establish
  that generation is unavailable: trials or invoiced billing may still apply.
  Billing mode is not returned; do not infer it from cash or trial fields.
  Let the generation service enforce billing for an authorized request.

## Insufficient credits and returning users

- Distinguish `trial_exhausted`, `insufficient_balance`, unavailable service,
  authentication failure, and a failed generation. Do not describe every
  failure as exhausted credits.
- After a confirmed credit rejection, refresh `get_account_services` once
  to report current balance and the relevant trial count. If lookup fails,
  keep the original error and say balance is unavailable; do not fabricate
  zero or keep retrying. The read-only refresh does not restart generation.
- For a confirmed rejection before task creation, say generation did not start.
  Report no charge only when the response establishes that. For an existing
  failed task, use its `refunded` value; do not infer a refund from failure alone.
- Do not automatically retry a credit error, swap to another endpoint to get
  another free run, or invite a new account to bypass limits.
- If the user says account access or credits have changed and asks to continue,
  refresh account services. Reuse the prior source and intended parameters
  from this conversation. Retrieve any existing task first. A confirmed
  rejected submission can be submitted once after the new request, with
  billing enforced by the server. Report any freshly returned cash balance,
  but do not claim “your balance is sufficient” from that snapshot alone.
- If prior context is missing, ask for the source file, URL, or task ID. Do not claim
  persistent cross-conversation memory or ask the user to repeat known inputs.

## Balance and free-trial help

- After an actual `insufficient_balance` or `trial_exhausted` rejection, add
  one link to the published **Balance and free trials** guide below. Also use
  it when the user asks how balance or trial limits work. Explain the actual
  error first; do not append the link to every successful generation.
- Use the conversation language, not a guessed location. For Traditional
  Chinese use `zh-HK`, for Simplified Chinese use `zh`. For other unsupported
  languages or an unclear language, use the English page. Translate the link
  label naturally; do not invent a translated URL slug.

| Language | Guide URL |
| --- | --- |
| English / fallback | https://platform.sonilo.com/usage-and-entitlements |
| 简体中文 | https://platform.sonilo.com/zh/usage-and-entitlements |
| 繁體中文 | https://platform.sonilo.com/zh-HK/usage-and-entitlements |
| German | https://platform.sonilo.com/de/usage-and-entitlements |
| Spanish | https://platform.sonilo.com/es/usage-and-entitlements |
| French | https://platform.sonilo.com/fr/usage-and-entitlements |
| Italian | https://platform.sonilo.com/it/usage-and-entitlements |
| Japanese | https://platform.sonilo.com/ja/usage-and-entitlements |
| Korean | https://platform.sonilo.com/ko/usage-and-entitlements |
| Portuguese | https://platform.sonilo.com/pt/usage-and-entitlements |

- The guide is a public explanation, not an account lookup. Do not put
  balances, account IDs, media URLs, task IDs, or credentials in its URL.
  Do not claim it displays the user's live balance or updates their account.
- Link to the explanation with labels such as “Balance and free trials” or
  “余额与免费试用”. Do not describe the link as a payment button. After the
  user reports an account update and asks to continue, follow the task-check
  flow above.
- Authentication errors require reconnecting the Platform account; service
  outages and failed tasks need their actual error explained. Do not treat
  these as balance errors or replace their next steps with this guide.

## Paying for more

- Explain the actual error first, and do not turn a failed request into a
  sales pitch. Do not promote upgrades, plans, or top-ups the user did not
  ask about.
- When a tool response includes its own instructions or link for adding
  funds, relay them as returned. Do not invent a pricing, checkout, or
  billing URL, and do not guess prices.
- If the user asks how to add funds and no tool response has said, point them
  to their Sonilo Platform account at https://platform.sonilo.com.
- For an explicit request for product guidance or examples, the public
  [Sonilo MCP guide](https://platform.sonilo.com/mcp) is available. Use it for
  learning the product, not as the response to an exhausted-credit error.
