import discord as d
from discord.ext import commands as c

from utils.db_operations import (
    fetch_server_settings,
)
from utils.permissions import has_doam_permission
from utils.responses import CommandResponse


class Derby(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    derby = d.SlashCommandGroup(
        "derby",
        "Start or end a DOAM Derby",
    )

    @derby.command(
        name="start",
        description="Start a DOAM Derby.",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="pitches",
        description="The number of pitches each player should receive.",
        input_type=d.SlashCommandOptionType.integer,
        min_value=20,
        max_value=100,
        required=True,
    )
    async def start(
        self,
        ctx: d.ApplicationContext,
        pitches: int,
    ):
        settings = fetch_server_settings(ctx)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        if not has_doam_permission(ctx.author, settings, self.bot):
            return await ctx.respond(
                str(CommandResponse.MISSING_START_PERM),
                ephemeral=True,
            )


def setup(bot: d.Bot):
    bot.add_cog(Derby(bot))
