from __future__ import annotations

import argparse
import asyncio
import logging
import os
from dataclasses import replace
from pathlib import Path

from dotenv import load_dotenv

from newsbot.config import load_settings
from newsbot.db import Store
from newsbot.digest import build_digest


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _load_env() -> None:
    for candidate in (Path("/etc/newsbot.env"), Path(".env")):
        if candidate.exists():
            load_dotenv(candidate, override=False)


async def print_digest() -> None:
    settings = load_settings()
    db_path = settings.db_path
    parent = db_path.parent
    if not parent.exists() or not os.access(parent, os.W_OK):
        settings = replace(settings, db_path=Path("./seen.sqlite"))
    store = Store(settings.db_path)
    try:
        messages, selected, skipped = await build_digest(settings, store, mark_seen=False)
        print(f"# items={len(selected)} skipped={skipped}\n")
        for message in messages:
            print(message)
            print("\n----\n")
    finally:
        store.close()


def run_bot() -> None:
    from newsbot.bot import build_application

    settings = load_settings()
    store = Store(settings.db_path)
    application = build_application(settings, store)
    logging.getLogger("newsbot").info(
        "starting bot tz=%s daily=%02d:%02d feeds=%s",
        settings.timezone,
        settings.digest_hour,
        settings.digest_minute,
        settings.feeds_path,
    )
    application.run_polling(drop_pending_updates=True)


def main() -> None:
    _configure_logging()
    _load_env()
    parser = argparse.ArgumentParser(description="Daily news digest Telegram bot")
    parser.add_argument("--print", action="store_true", help="Fetch and print a digest without Telegram")
    args = parser.parse_args()
    if args.print:
        asyncio.run(print_digest())
        return
    run_bot()


if __name__ == "__main__":
    main()
