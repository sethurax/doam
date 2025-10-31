import discord as d
from discord.ext import commands as c

from utils.db_operations import fetch_server_settings, set_server_settings
from utils.embeds import generate_settings_embed


class Setup(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    settings = d.SlashCommandGroup(
        "settings",
        "View and manage DOAM Bot settings for the current server.",
    )

    @settings.command(
        name="view",
        description="View the DOAM Bot settings for the current server.",
        contexts=[d.InteractionContextType.guild],
    )
    async def view(self, ctx: d.ApplicationContext):
        settings = fetch_server_settings(ctx)
        if not settings:
            await ctx.respond(
                "No settings found for this server. Please run `/settings set` to get started!",
                ephemeral=True,
            )
            return

        await ctx.respond(
            embeds=[generate_settings_embed(ctx, settings)],
            ephemeral=True,
        )

    @settings.command(
        name="set",
        description="Register your server, or update server settings.",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="channel",
        description="Restrict DOAMs to a specific channel.",
        input_type=d.SlashCommandOptionType.channel,
        channel_types=[d.ChannelType.text],
        required=False,
    )
    @d.option(
        name="derby_channel",
        description="The channel where the DOAM derby scoreboard will be shown.",
        input_type=d.SlashCommandOptionType.channel,
        channel_types=[d.ChannelType.text],
        required=False,
    )
    @d.option(
        name="admin_role",
        description="Restrict starting DOAMs/derbies to a specific role.",
        input_type=d.SlashCommandOptionType.role,
        required=False,
    )
    @d.option(
        name="ping_role",
        description="The role to ping when starting a DOAM.",
        input_type=d.SlashCommandOptionType.role,
        required=False,
    )
    async def set(
        self,
        ctx: d.ApplicationContext,
        channel: d.abc.GuildChannel | None = None,
        derby_channel: d.TextChannel | None = None,
        admin_role: d.Role | None = None,
        ping_role: d.Role | None = None,
    ):
        updated = set_server_settings(
            ctx, channel, derby_channel, admin_role, ping_role
        )

        return await ctx.respond(
            embeds=[
                generate_settings_embed(ctx, updated),
            ],
        )


def setup(bot: d.Bot):
    bot.add_cog(Setup(bot))
