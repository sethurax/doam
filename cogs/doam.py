import os
import random
from datetime import datetime

import discord as d
import discord.ext.pages as p
from discord.ext import commands as c

from db import r
from utils.db_operations import (
    fetch_server_settings,
    fetch_active_doam,
    register_doam,
    delete_doam_data,
    set_pitch,
)
from utils.diff import calculate_diff
from utils.embeds import generate_doam_start_embed
from utils.permissions import has_doam_permission
from utils.responses import CommandResponse


class Doam(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    doam = d.SlashCommandGroup(
        "doam",
        "Start or end a DOAM.",
    )

    @doam.command(
        name="start",
        description="Start a DOAM.",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="player1",
        description="The first player in the DOAM.",
        input_type=d.SlashCommandOptionType.user,
    )
    @d.option(
        name="player2",
        description="The second player in the DOAM.",
        input_type=d.SlashCommandOptionType.user,
    )
    async def start(
        self,
        ctx: d.ApplicationContext,
        player1: d.Member,
        player2: d.Member,
    ):
        settings = fetch_server_settings(ctx)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        if not has_doam_permission(ctx.author, settings, self.bot):
            return await ctx.respond(
                str(CommandResponse.MISSING_START_PERM),
                ephemeral=True,
            )

        doam = fetch_active_doam(ctx.guild.id)
        if doam:
            return await ctx.respond(
                str(CommandResponse.ACTIVE_DOAM),
                ephemeral=True,
            )

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)

        players = [player1, player2]
        random.shuffle(players)

        await channel.send(
            content=(f"<@&{settings['ping_role']}>" if settings["ping_role"] else ""),
            embeds=[generate_doam_start_embed(ctx, players)],
        )
        await channel.send("# ROUND 1")
        await channel.send(f"{players[0].mention} - use `/p` to submit your pitch!")

        register_doam(ctx, players[0], players[1])
        return await ctx.respond(str(CommandResponse.DOAM_STARTED), ephemeral=True)

    @doam.command(
        name="end",
        description="End the currently running DOAM.",
        contexts=[d.InteractionContextType.guild],
    )
    async def end(self, ctx: d.ApplicationContext):
        settings = fetch_server_settings(ctx)

        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        if not has_doam_permission(ctx.author, settings, self.bot):
            return await ctx.respond(
                str(CommandResponse.MISSING_END_PERM),
                ephemeral=True,
            )

        doam = fetch_active_doam(ctx.guild.id)
        if not doam:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DOAM),
                ephemeral=True,
            )

        delete_doam_data(ctx)

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)
        await channel.send(f"DOAM ended by {ctx.author.mention}")
        return await ctx.respond(CommandResponse.DOAM_ENDED, ephemeral=True)

    @d.slash_command(
        name="p",
        description="Throw a pitch!",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="num",
        description="The pitch number you want to submit.",
        input_type=d.SlashCommandOptionType.integer,
        min_value=1,
        max_value=1000,
        required=True,
    )
    async def p(self, ctx: d.ApplicationContext, num: int):
        settings = fetch_server_settings(ctx)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        doam = fetch_active_doam(ctx.guild.id)
        if not doam:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DOAM),
                ephemeral=True,
            )

        if int(doam["pitching"]) != ctx.author.id:
            return await ctx.respond(str(CommandResponse.NOT_PITCHER), ephemeral=True)

        if int(doam["pitch"]) != 0:
            set_pitch(ctx, num)
            return await ctx.respond("Pitch updated!", ephemeral=True)

        await ctx.delete()

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)
        await channel.send(
            f"<@{doam['hitting']}> - the pitch is in! Use `/s` to submit your swing."
        )

        return set_pitch(ctx, num)

    @d.slash_command(
        name="s",
        description="Swing the bat!",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="num",
        description="The swing number you want to submit.",
        input_type=d.SlashCommandOptionType.integer,
        min_value=1,
        max_value=1000,
        required=True,
    )
    async def s(self, ctx: d.ApplicationContext, num: int):
        settings = fetch_server_settings(ctx)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        doam = fetch_active_doam(ctx.guild.id)
        if not doam:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DOAM),
                ephemeral=True,
            )

        if int(doam["hitting"]) != ctx.author.id:
            return await ctx.respond(str(CommandResponse.NOT_HITTER), ephemeral=True)

        if int(doam["pitch"]) == 0:
            return await ctx.respond(str(CommandResponse.NO_SWING_YET), ephemeral=True)

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)

        diff = calculate_diff(int(doam["pitch"]), num)

        # TODO: can probably split this out into separate modules for updating scores, logging results
        if diff <= 100:
            if int(doam["hitting"]) == int(doam["player1"]):
                r.hincrby(f"doam:{ctx.guild.id}", "p1_score", 1)
                r.lpush(
                    f"p1_hitting:{ctx.guild.id}",
                    f"{doam['pitch']:<8}{str(num):<8}{str(diff):<7}HR   ",
                )
            else:
                r.hincrby(f"doam:{ctx.guild.id}", "p2_score", 1)
                r.lpush(
                    f"p2_hitting:{ctx.guild.id}",
                    f"{doam['pitch']:<8}{str(num):<8}{str(diff):<7}HR   ",
                )
        else:
            if doam["hitting"] == doam["player1"]:
                r.lpush(
                    f"p1_hitting:{ctx.guild.id}",
                    f"{doam['pitch']:<8}{str(num):<8}{str(diff):<7}--   ",
                )
            else:
                r.lpush(
                    f"p2_hitting:{ctx.guild.id}",
                    f"{doam['pitch']:<8}{str(num):<8}{str(diff):<7}--   ",
                )

        doam = fetch_active_doam(ctx.guild.id)

        await channel.send(
            embeds=[
                d.Embed(
                    title=f"Round {doam['round']}",
                    fields=[
                        d.EmbedField(
                            name="Result:",
                            value=f"```Pitch:  {doam['pitch']}\nSwing:  {num}\n\nDiff:   {diff}\n\nResult: {"HR" if diff <= 100 else "No HR"}```",
                        ),
                        d.EmbedField(
                            name=f"Scores After Round {doam['round']}:",
                            value=f"{doam['p1_name']} - {doam['p1_score']}\n{doam['p2_name']} - {doam['p2_score']}",
                        ),
                    ],
                    timestamp=datetime.now(),
                    footer=d.EmbedFooter(
                        text="Questions? Issues? Use /help",
                    ),
                )
            ]
        )

        game_ends = False

        if int(doam["p1_score"]) > int(doam["p2_score"]):
            game_ends = True

        chase_rounds = 10 - int(doam["round"])
        if (
            int(doam["round"]) < 10
            and doam["hitting"] == doam["player1"]
            and int(doam["p1_score"]) < int(doam["p2_score"])
        ):
            if int(doam["p2_score"]) - int(doam["p1_score"]) > chase_rounds:
                game_ends = True

        if (
            int(doam["round"]) >= 10
            and doam["player1"] == doam["hitting"]
            and int(doam["p1_score"]) != int(doam["p2_score"])
        ):
            game_ends = True

        if game_ends:
            winner = (
                doam["p1_name"]
                if int(doam["p1_score"]) > int(doam["p2_score"])
                else doam["p2_name"]
            )
            winner_logo = (
                doam["p1_avatar"]
                if int(doam["p1_score"]) > int(doam["p2_score"])
                else doam["p2_avatar"]
            )

            if winner == doam["p1_name"]:
                doam["p1_score"] = f"**{doam['p1_score']}**"
            else:
                doam["p2_score"] = f"**{doam['p2_score']}**"

            p1_hitting = r.lrange(f"p1_hitting:{ctx.guild.id}", 0, -1)
            p2_hitting = r.lrange(f"p2_hitting:{ctx.guild.id}", 0, -1)

            summary_pages = [
                p.Page(
                    embeds=[
                        d.Embed(
                            title=f"{winner} wins!",
                            description=f"Total rounds: {doam['round']}",
                            fields=[
                                d.EmbedField(
                                    name="Final Score:",
                                    value=f"{doam['p1_name']} - {doam['p1_score']}\n{doam['p2_name']} - {doam['p2_score']}",
                                )
                            ],
                            timestamp=datetime.now(),
                            thumbnail=winner_logo or os.getenv("LOGO", "") or None,
                            footer=d.EmbedFooter(
                                text="Questions? Issues? Use /help",
                            ),
                        )
                    ]
                ),
                p.Page(
                    embeds=[
                        d.Embed(
                            title=f"{doam["p1_name"]}",
                            description=f"Batting Results\n```{"\n".join(p1_hitting[::-1])}```",
                            timestamp=datetime.now(),
                            footer=d.EmbedFooter(
                                text="Questions? Issues? Use /help",
                            ),
                        )
                    ]
                ),
                p.Page(
                    embeds=[
                        d.Embed(
                            title=f"{doam["p2_name"]}",
                            description=f"Batting Results\n```{"\n".join(p2_hitting[::-1])}```",
                            timestamp=datetime.now(),
                            footer=d.EmbedFooter(
                                text="Questions? Issues? Use /help",
                            ),
                        )
                    ]
                ),
            ]

            summary = p.Paginator(
                pages=summary_pages,
                timeout=None,
                show_disabled=False,
                author_check=False,
            )

            delete_doam_data(ctx)

            return await summary.respond(
                interaction=ctx.interaction,
                target=channel,
                target_message="Game over! Generating summary...",
            )

        if int(doam["round"]) < 10:
            r.hset(
                f"doam:{ctx.guild.id}",
                mapping={"round": int(doam["round"]) + 1, "pitch": 0},
            )

        if int(doam["round"]) == 10:
            if doam["hitting"] == doam["player2"]:
                await channel.send("# SWITCHING SIDES")
                r.hset(
                    f"doam:{ctx.guild.id}",
                    mapping={
                        "round": 1,
                        "pitching": doam["hitting"],
                        "hitting": doam["pitching"],
                        "pitch": 0,
                    },
                )
            else:
                await channel.send("# SWITCHING SIDES")
                r.hset(
                    f"doam:{ctx.guild.id}",
                    mapping={
                        "round": 11,
                        "pitching": doam["hitting"],
                        "hitting": doam["pitching"],
                        "pitch": 0,
                    },
                )

        if int(doam["round"]) >= 11:
            if doam["hitting"] == doam["player1"]:
                await channel.send("# SWITCHING SIDES")
                r.hset(
                    f"doam:{ctx.guild.id}",
                    mapping={"round": int(doam["round"]) + 1, "pitch": 0},
                )
            else:
                await channel.send("# SWITCHING SIDES")

            r.hset(
                f"doam:{ctx.guild.id}",
                mapping={
                    "pitching": doam["hitting"],
                    "hitting": doam["pitching"],
                    "pitch": 0,
                },
            )

        updated_data2 = r.hgetall(f"doam:{ctx.guild.id}")
        await channel.send(f"# ROUND {updated_data2['round']}")
        return await channel.send(
            f"<@{updated_data2["pitching"]}> - use `/p` to submit your pitch!"
        )


def setup(bot: d.Bot):
    bot.add_cog(Doam(bot))
