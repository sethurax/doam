import os

import discord

from db import db

bot = discord.Bot(owner_id=int(os.getenv("OWNER", "")))

if __name__ == "__main__":
    # Since all bot functionality relies on database connection, we can exit early if the connection fails
    if not db.ping():
        print("Redis connection failed.")
        exit(1)

    for file in os.scandir("cogs"):
        bot.load_extension(f"cogs.{file.name[:-3]}")
        print(f"Cog loaded: {file.name}")

    bot.run(os.getenv("TOKEN", ""))
