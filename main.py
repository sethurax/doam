import os
import discord
from db import db

bot = (
    discord.Bot(owner_id=int(os.getenv("OWNER", "")))
    if os.getenv("BRANCH") == "main"
    else discord.Bot(
        debug_guilds=[int(os.getenv("DEBUG_GUILD", ""))],
        owner_id=int(os.getenv("OWNER", "")),
    )
)

if __name__ == "__main__":
    # Since all bot functionality relies on database connection, exit early if the connection fails
    if not db.ping():
        print("Redis connection failed.")
        exit(1)

    for file in os.scandir("cogs"):
        bot.load_extension(f"cogs.{file.name[:-3]}")
        print(f"Cog loaded: {file.name}")

    bot.run(os.getenv("TOKEN", ""))
