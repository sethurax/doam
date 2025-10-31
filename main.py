import os

import discord

from db import r, test_redis_connection

bot = discord.Bot(owner_id=int(os.getenv("OWNER", "")))

cogs_list = ["setup", "doam", "events"]
for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

if __name__ == "__main__":
    test_redis_connection(r)
    bot.run(os.getenv("TOKEN", ""))
