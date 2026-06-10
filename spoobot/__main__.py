from __future__ import annotations

import asyncio

from spoobot.bot import SpooBot
from spoobot.config import load_config
from spoobot.infrastructure.logging import setup_logging


async def main() -> None:
    setup_logging()
    config = load_config()
    bot = SpooBot(config)
    async with bot:
        await bot.start(config.bot.bot_token)


if __name__ == "__main__":
    asyncio.run(main())
