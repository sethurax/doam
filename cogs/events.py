import time
import discord as d
from discord.ext import commands as c


class EventsCog(c.Cog):
    def __init__(self, bot: d.Bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_ready(self):
        if not isinstance(self.bot.user, d.ClientUser):
            print(
                f"{time.strftime('%H:%M:%S', time.localtime())}: Logged in; client information unknown."
            )
            return

        await self.bot.change_presence(status=d.Status.online, activity=d.Game("doam."))

        print(
            f"{time.strftime('%H:%M:%S', time.localtime())}: Logged in as {self.bot.user} (ID: {self.bot.user.id})"
        )

    @c.Cog.listener()
    async def on_application_command(self, ctx: d.ApplicationContext):
        if not isinstance(ctx.command, d.ApplicationCommand):
            print(
                f"{time.strftime('%H:%M:%S', time.localtime())}: Command information unkown."
            )
            return

        print(
            f"{time.strftime('%H:%M:%S', time.localtime())}: Command: /{ctx.command.qualified_name} | Guild: {ctx.guild.name if ctx.guild else 'DM'} | User: {ctx.author.display_name}"
        )

    @c.Cog.listener()
    async def on_guild_join(self, guild: d.Guild):
        print(
            f"{time.strftime('%H:%M:%S', time.localtime())}: Bot joined to new guild - {guild.name} ({guild.id})"
        )

        if not isinstance(self.bot.owner_id, int):
            return

        owner = self.bot.get_user(self.bot.owner_id)

        if isinstance(owner, d.User):
            return await owner.send(
                f"Bot joined to new guild: {guild.name} ({guild.id})"
            )


def setup(bot: d.Bot):
    bot.add_cog(EventsCog(bot))
