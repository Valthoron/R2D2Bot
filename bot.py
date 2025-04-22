import asyncio
import os

import discord

from aiohttp_socks import ProxyConnector
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PROXY = os.getenv("PROXY") or None


class Artoo(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    async def on_message(self, message):
        ctx = await self.get_context(message)
        if ctx.valid:
            await self.invoke(ctx)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return

        raise error


async def main():
    intents = discord.Intents(messages=True, message_content=True)
    proxy = None
    connector = None

    if (PROXY and PROXY.startswith("socks5://")):
        connector = ProxyConnector.from_url(PROXY)
    elif (PROXY):
        proxy = PROXY

    bot = Artoo(command_prefix="!", intents=intents, activity=discord.Game(name="Star Wars RPG D6"), proxy=proxy, connector=connector)
    await bot.load_extension("cogs.dice")
    await bot.load_extension("cogs.species_pictures")
    await bot.start(DISCORD_BOT_TOKEN)

try:
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(main())
except KeyboardInterrupt:
    pass
