import time
import discord as d
from discord.ext import commands as c


class EventsCog(c.Cog):
    def __init__(self, bot: d.Bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=d.Status.online, activity=d.Game("doam."))

        if self.bot is d.ClientUser:
            print(
                f"{time.strftime('%H:%M:%S', time.localtime())}: Logged in as {self.bot.user} (ID: {self.bot.user.id})"
            )
        else:
            print(
                f"{time.strftime('%H:%M:%S', time.localtime())}: Logged in; client information unknown."
            )

    @c.Cog.listener()
    async def on_application_command(self, ctx: d.ApplicationContext):
        if ctx.command is d.ApplicationCommand:
            print(
                f"{time.strftime('%H:%M:%S', time.localtime())}: Command: /{ctx.command.qualified_name} | Guild: {ctx.guild.name if ctx.guild else 'DM'} | User: {ctx.author.display_name}"
            )
        else:
            print(f"{time.strftime('%H:%M:%S', time.localtime())}: Command: unknown")

    @c.Cog.listener()
    async def on_guild_join(self, guild: d.Guild):
        print(
            f"{time.strftime('%H:%M:%S', time.localtime())}: Bot joined to new guild - {guild.name} ({guild.id})"
        )

        if self.bot.owner_id is int:
            owner = self.bot.get_user(self.bot.owner_id)
            if owner is d.User:
                await owner.send(f"Bot joined to new guild: {guild.name} ({guild.id})")


def setup(bot: d.Bot):
    bot.add_cog(EventsCog(bot))
