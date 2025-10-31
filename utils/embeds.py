import os
from datetime import datetime

import discord as d


def generate_settings_embed(ctx: d.ApplicationContext, settings: dict):
    return d.Embed(
        title=f"Server Settings: {ctx.guild.name}",
        fields=[
            d.EmbedField(
                name="Channel Restriction",
                value=(f"<#{settings['channel']}>" if settings["channel"] else "None"),
            ),
            d.EmbedField(
                name="Derby Scoreboard Channel",
                value=(
                    f"<#{settings['derby_channel']}>"
                    if settings["derby_channel"]
                    else "None"
                ),
            ),
            d.EmbedField(
                name="Admin Role Restriction",
                value=(
                    f"<@&{settings['admin_role']}>"
                    if settings["admin_role"]
                    else "None"
                ),
            ),
            d.EmbedField(
                name="Ping Role on DOAM Start",
                value=(
                    f"<@&{settings['ping_role']}>" if settings["ping_role"] else "None"
                ),
            ),
        ],
        thumbnail=(ctx.guild.icon.url if ctx.guild.icon else os.getenv("LOGO", "")),
        timestamp=datetime.now(),
    )


def generate_doam_start_embed(ctx: d.ApplicationContext, players: list):
    return d.Embed(
        title="A new DOAM has been started!",
        description="Player order (decided at random):",
        fields=[
            d.EmbedField(
                name="Player 1 | Pitching First",
                value=f"{players[0].mention}",
            ),
            d.EmbedField(
                name="Player 2 | Hitting First",
                value=f"{players[1].mention}",
            ),
        ],
        image=os.getenv("LOGO", ""),
        timestamp=datetime.now(),
    )
