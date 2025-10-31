import time

import discord as d
from discord.ext import commands as c


class EventsCog(c.Cog):
    def __init__(self, bot: d.Bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_ready(self):
        print(
            f"Logged in as {self.bot.user} (ID: {self.bot.user.id if self.bot.user.id is not None else 'N/A'})"
        )

    @c.Cog.listener()
    async def on_application_command(self, ctx: d.ApplicationContext):
        print(
            f"Time: {time.strftime('%H:%M:%S', time.localtime())} | Command: /{ctx.command.qualified_name} | Guild: {ctx.guild.name if ctx.guild else 'DM'} | User: {ctx.author.display_name}"
        )

    @c.Cog.listener()
    async def on_guild_join(self, guild: d.Guild):
        owner = self.bot.get_user(self.bot.owner_id)
        await owner.send(f"Bot joined to new guild: {guild.name} ({guild.id})")


def setup(bot: d.Bot):
    bot.add_cog(EventsCog(bot))
