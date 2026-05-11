# Categories

The canonical PII taxonomy used across all sub-benches.

## The 12 canonical categories

| Label | Description | Examples |
|---|---|---|
| `private_person` | Real person names | "Marcus Chen", "田中 雄一", "김지은" |
| `private_email` | Email addresses | `marcus@helios-ai.example`, `tanaka.yuichi@example.co.jp` |
| `private_phone` | Phone numbers | `+1-415-555-0142`, `+44 20 7946 0958` |
| `private_address` | Street addresses or sufficiently-precise locations | `350 5th Ave, NYC`, `1-1-1 Marunouchi, Chiyoda-ku, Tokyo` |
| `private_url` | URLs that identify a person, account, or non-public resource | `notion.so/u/marcus-chen`, `github.com/user/private-repo` |
| `private_company` | Specific real or pseudonymous company names in private contexts | "Helios AI", "Acme Realty" — NOT vendor brand names like "Slack", "Outlook" |
| `private_repo` | Code repository identifiers in private contexts | `screenpipe/internal-tools`, `gracenote/staging` |
| `private_handle` | Social or platform handles | `@marcus_chen`, `discord:notmarcus#1234` |
| `private_channel` | Slack / Discord / Teams channel names that imply project or person | `#compai-tessera`, `#deal-acme-h2-2026` |
| `private_id` | Government, account, employee, or transaction IDs | `SSN 123-45-6789`, `EMP-00482`, `INV-2026-0142` |
| `private_date` | Dates that identify a person (DOB) or sensitive event | `DOB 1985-03-14`, `terminated 2025-09-12` |
| `secret` | Passwords, API keys, JWTs, DB connection strings, private keys | `sk-proj-...`, `Bearer eyJhbGc...`, `-----BEGIN PRIVATE KEY-----` |

## Per-bench coverage

| Category | text/ | image/ | trace/ |
|---|:---:|:---:|:---:|
| private_person | ✅ | ✅ | ✅ |
| private_email | ✅ | ✅ | ✅ |
| private_phone | ✅ | ✅ | ✅ |
| private_address | ✅ | ✅ | ✅ |
| private_url | ✅ | ✅ | ✅ |
| private_company | ✅ | ✅ | ✅ |
| private_repo | ✅ | ✅ | ✅ |
| private_handle | ✅ | ⚠️ | ✅ |
| private_channel | ✅ | ✅ | ✅ |
| private_id | ✅ | ⚠️ | ✅ |
| private_date | ✅ | ⚠️ | ✅ |
| secret | ✅ | ✅ | ✅ |

⚠️ = present in taxonomy but **not yet in image bench corpus**. v1 ships with this asymmetry documented; backport is on the post-v0.1 roadmap. See [LIMITATIONS.md](./LIMITATIONS.md).

## What each category does NOT include

- `private_person` does **not** include brand names. "Claude", "Raycast", "Linear" are products, not people. This is the canonical confusion that base-OPF and Presidio fail on; we hold strict.
- `private_company` does **not** include vendor names of the app being used. The string "Slack" in a Slack title is the app name, not PII. The string "Helios AI" inside a Slack message IS PII (it's the user's customer / employer / target).
- `private_url` does **not** include public URLs (`github.com`, `wikipedia.org`, `slack.com`). Inclusion criterion: does the URL identify a private entity (private repo, individual user profile, etc.)?
- `private_handle` does **not** include `@everyone`, `@here`, or app-internal mentions. Only persistent identifiers.
- `secret` does **not** include the *labels* of secrets ("API_KEY", "Bearer token") — only the secret values themselves.

## Why these 12 and not more

Earlier drafts had `private_account_number` and `private_medical_record` as separate categories. We collapsed:
- `private_account_number` → `private_id` (one ID category, one secret category, simpler)
- `private_medical_record` → `secret` for sensitive clinical data, `private_id` for MRN strings

This matches the upstream OpenAI Privacy Filter taxonomy. Diverging would force us to retrain rather than fine-tune.

## Adding a category

If you want to add a new category (e.g. `private_biometric`, `private_genetic`):

1. Update this file
2. Update `text/CATEGORIES.md` and `image/CATEGORIES.md`
3. Update each adapter's `LABEL_MAP` to map your model's output to the new canonical
4. Re-run the leaderboard
5. Add a `CHANGELOG.md` entry

We will not accept PRs that add categories without re-running the full leaderboard against all current adapters.
