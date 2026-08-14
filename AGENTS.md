# AGENTS.md

## Cursor Cloud specific instructions

### What this project is
A self-hosted **daily news digest bot** (Python). It fetches public RSS feeds
(defined in `newsbot/feeds.yaml`), dedupes them via SQLite, adds US-stock / gold /
sector market quotes and a rotating English study plan, renders an HTML+plaintext
digest, and delivers it by **email (SMTP)** and/or **Telegram**. Entry point is the
`newsbot` package run as a module (`python -m newsbot`), see `newsbot/__main__.py`.

### Environment / setup
- Python 3.12 with a virtualenv at `.venv` (the startup update script creates it and
  installs `requirements.txt`). Run everything through `.venv/bin/python`.
- There is **no test suite and no configured linter**. For a lightweight sanity
  check use `.venv/bin/python -m compileall newsbot`. There is no build step.

### Running / smoke test (no credentials needed)
- `.venv/bin/python -m newsbot --print` fetches live RSS + market data and prints
  the rendered digest. This is the best end-to-end smoke test and needs **no**
  SMTP/Telegram secrets. It requires outbound internet.

### Non-obvious gotchas
- `--send` (send email now) and the default service mode (`python -m newsbot`, no
  flags) require a delivery channel to be configured or they exit with an error:
  set `MAIL_TO` + `SMTP_PASSWORD` for email, and/or `TELEGRAM_BOT_TOKEN` for
  Telegram. Config is read from environment variables, loaded from `/etc/newsbot.env`
  or a local `.env` (see `.env.example`). `--print` never sends and ignores these.
- `NEWSBOT_DB` defaults to `/var/lib/newsbot/seen.sqlite`. For `--print`/`--send`
  the code automatically falls back to `./seen.sqlite` when that path is not
  writable, so it works fine in a dev checkout. The long-running service mode does
  **not** fall back — set `NEWSBOT_DB` to a writable path when running it locally.
- Market quotes come from eastmoney endpoints that frequently return HTTP 502; the
  code retries and falls back to `push2delay.eastmoney.com`, so transient 502 log
  lines during `--print` are expected, not failures.
- `deploy/install.sh` + `deploy/newsbot.service` are for production VPS deployment
  via systemd and are not needed for local development.
