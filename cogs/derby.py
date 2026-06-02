import asyncio

import discord as d
from discord.ext import commands as c

from db import db
from utils.db_operations import (
    fetch_server_settings,
    fetch_active_derby,
    register_derby,
    delete_derby_data,
)
from utils.diff import calculate_diff
from utils.embeds import generate_derby_start_embed
from utils.permissions import has_doam_permission
from utils.responses import CommandResponse


class Derby(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    derby = d.SlashCommandGroup(
        "derby",
        "Start or end a DOAM Run Derby.",
    )

    @derby.command(
        name="start",
        description="Start a DOAM Run Derby.",
        contexts=[d.InteractionContextType.guild],
    )
    @d.option(
        name="pitcher",
        description="The pitcher for the derby.",
        input_type=d.SlashCommandOptionType.user,
    )
    @d.option(
        name="pitches",
        description="The number of pitches (max one pitch per minute)",
        input_type=d.SlashCommandOptionType.integer,
        min_value=5,
        max_value=60,
        required=True,
    )
    async def start(self, ctx: d.ApplicationContext, pitcher: d.Member, pitches: int):
        settings = fetch_server_settings(ctx.guild.id)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        if not has_doam_permission(ctx.author, settings, self.bot):
            return await ctx.respond(
                str(CommandResponse.MISSING_START_PERM),
                ephemeral=True,
            )

        derby = fetch_active_derby(ctx.guild.id)
        if derby:
            return await ctx.respond(
                str(CommandResponse.ACTIVE_DERBY),
                ephemeral=True,
            )

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)

        await channel.send(
            content=(f"<@&{settings['ping_role']}>" if settings["ping_role"] else ""),
            embeds=[generate_derby_start_embed(ctx, pitcher, pitches)],
        )
        await channel.send(f"{pitcher.mention} - use `/dp` to submit your first pitch!")

        register_derby(ctx, pitcher, pitches)
        return await ctx.respond(str(CommandResponse.DERBY_STARTED), ephemeral=True)

    @derby.command(
        name="end",
        description="End the currently running DOAM Run Derby.",
        contexts=[d.InteractionContextType.guild],
    )
    async def end(self, ctx: d.ApplicationContext):

        settings = fetch_server_settings(ctx.guild.id)

        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        if not has_doam_permission(ctx.author, settings, self.bot):
            return await ctx.respond(
                str(CommandResponse.MISSING_END_PERM),
                ephemeral=True,
            )

        derby = fetch_active_derby(ctx.guild.id)
        if not derby:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DERBY),
                ephemeral=True,
            )

        delete_derby_data(ctx)

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)
        await channel.send(f"DOAM Run Derby ended by {ctx.author.mention}")
        return await ctx.respond(CommandResponse.DERBY_ENDED, ephemeral=True)

    @d.slash_command(
        name="dp",
        description="Throw a derby pitch!",
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
    async def dp(self, ctx: d.ApplicationContext, num: int):

        settings = fetch_server_settings(ctx.guild.id)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        derby = fetch_active_derby(ctx.guild.id)
        if not derby:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DERBY),
                ephemeral=True,
            )

        if int(derby["pitcher"]) != ctx.author.id:
            return await ctx.respond(
                str(CommandResponse.NOT_DERBY_PITCHER), ephemeral=True
            )

        if derby["pitch_allowed"] != "yes":
            return await ctx.respond(
                "You must wait at least one minute between pitches - you will get a ping when it's time!",
                ephemeral=True,
            )

        await ctx.respond("Pitch submitted!", ephemeral=True)

        channel = self.bot.get_channel(int(settings["channel"]) or ctx.channel.id)

        # if second pitch or more, build previous round results
        if int(derby["round"]) >= 1:
            rd = str(derby["round"])
            pitch = str(derby["pitch"])
            swings = int(derby["swing_count"])
            avg_diff = (
                round((int(derby["sum_diff"])) / swings)
                if int(derby["sum_diff"]) != 0
                else 0
            )
            hrs = derby["hrs"]

            round_results = f"{rd:<5}| {pitch:<4}| {swings:<4}| {avg_diff:<4}| {hrs:<4}"

            hitter_ids = db.smembers(f"derby_hitters:{ctx.guild.id}")
            pipe = db.pipeline()
            for user_id in hitter_ids:
                pipe.hgetall(f"derby_score:{user_id}")
            raw_results = pipe.execute()

            scores = []
            for user_id, hash_data in zip(hitter_ids, raw_results):
                if not hash_data:
                    continue
                scores.append(
                    {
                        "user_id": user_id,
                        "name": hash_data.get("name", ""),
                        "swings": int(hash_data.get("swings", 0)),
                        "total_diff": int(hash_data.get("total_diff", 0)),
                        "hrs": int(hash_data.get("hrs", 0)),
                    }
                )

            scoreboard = sorted(scores, key=lambda x: (-x["hrs"], x["name"]))
            scoreboard_string = "\n".join(
                f"{entry['name']:<32}{entry['hrs']:<3}" for entry in scoreboard
            )

            db.lpush(f"derby_results:{ctx.guild.id}", round_results)

            await channel.send(f"## Round {rd} Results")
            await channel.send(
                f"```-----------------------------\nRd   |  P  | #Sw | Dif | HRs \n-----------------------------\n{round_results}```"
            )

            await channel.send(f"## Leaderboard After Round {rd}")
            await channel.send(
                f"```{'Name':<32}HRs\n-----------------------------------\n{scoreboard_string}```"
            )

        # if current round number is less than limit, reset for next round:

        if int(derby["round"]) < int(derby["total_pitches"]):
            db.hset(
                f"derby:{ctx.guild.id}",
                mapping={
                    "round": int(derby["round"]) + 1,
                    "pitch": num,
                    "pitch_allowed": "no",
                    "swing_allowed": "yes",
                    "swing_count": 0,
                    "sum_diff": 0,
                    "hrs": 0,
                },
            )

            db.delete(f"derby_hitters_this_round:{ctx.guild.id}")

            await channel.send(
                f"# Round {int(derby['round']) + 1} of {derby['total_pitches']}"
            )
            await channel.send(
                "Hitters - the pitch is in! Use `/ds` to swing - you have 60 seconds, but not necessarily more!"
            )

            await asyncio.sleep(60)

            db.hset(f"derby:{ctx.guild.id}", mapping={"pitch_allowed": "yes"})

            return await channel.send(
                f"<@{derby['pitcher']}> - one minute has passed, you may submit your next pitch at any time."
            )

        # if current round number is exactly the limit, this is the last round
        if int(derby["round"]) == int(derby["total_pitches"]):
            db.hset(
                f"derby:{ctx.guild.id}",
                mapping={
                    "round": int(derby["round"]) + 1,
                    "pitch": num,
                    "pitch_allowed": "no",
                    "swing_count": 0,
                    "sum_diff": 0,
                    "hrs": 0,
                },
            )

            await channel.send(
                "Hitters - the pitch is in! Use `/ds` to swing - you have exactly 60 seconds, no more!"
            )

            await asyncio.sleep(60)

            db.hset(f"derby:{ctx.guild.id}", mapping={"swing_allowed": "no"})

            # TODO: compile and post game results

            rd = str(derby["round"])
            pitch = str(derby["pitch"])
            swings = int(derby["swing_count"])
            avg_diff = (
                round((int(derby["sum_diff"])) / swings)
                if int(derby["sum_diff"]) != 0
                else 0
            )
            hrs = derby["hrs"]

            round_results = f"{rd:<5}| {pitch:<4}| {swings:<4}| {avg_diff:<4}| {hrs:<4}"

            hitter_ids = db.smembers(f"derby_hitters:{ctx.guild.id}")
            pipe = db.pipeline()
            for user_id in hitter_ids:
                pipe.hgetall(f"derby_score:{user_id}")
            raw_results = pipe.execute()

            scores = []
            for user_id, hash_data in zip(hitter_ids, raw_results):
                if not hash_data:
                    continue
                scores.append(
                    {
                        "user_id": user_id,
                        "name": hash_data.get("name", ""),
                        "swings": int(hash_data.get("swings", 0)),
                        "total_diff": int(hash_data.get("total_diff", 0)),
                        "hrs": int(hash_data.get("hrs", 0)),
                    }
                )

            scoreboard = sorted(scores, key=lambda x: (-x["hrs"], x["name"]))
            scoreboard_string = "\n".join(
                f"{entry['name']:<32}{entry['hrs']:<3}" for entry in scoreboard
            )

            db.lpush(f"derby_results:{ctx.guild.id}", round_results)

            await channel.send(f"## Round {rd} Results")
            await channel.send(f"```{round_results}```")

            await channel.send("# Game Over! Final Results")
            await channel.send(f"```{'Name':<32}HRs\n{scoreboard_string}```")

    @d.slash_command(
        name="ds",
        description="Make a derby swing!",
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

        settings = fetch_server_settings(ctx.guild.id)
        if not settings:
            return await ctx.respond(str(CommandResponse.NO_SETTINGS), ephemeral=True)

        derby = fetch_active_derby(ctx.guild.id)
        if not derby:
            return await ctx.respond(
                str(CommandResponse.NO_ACTIVE_DERBY),
                ephemeral=True,
            )

        if derby["swing_allowed"] == "no":
            return await ctx.respond(
                str(CommandResponse.NO_DERBY_SWING), ephemeral=True
            )

        if (
            db.sismember(f"derby_hitters_this_round:{ctx.guild.id}", f"{ctx.user.id}")
            == 1
        ):
            return await ctx.respond(
                "You have already swung in this round of the derby. Please wait for next round before swinging again!",
                ephemeral=True,
            )

        diff = calculate_diff(int(derby["pitch"]), num)
        hrs = 1 if diff <= 100 else 0

        await ctx.respond(
            f"Diff: {diff} | Result: {'HR' if diff <= 100 else 'No HR'}. Pitch will be revealed at the end of the round!",
            ephemeral=True,
        )

        db.sadd(f"derby_hitters_this_round:{ctx.guild.id}", f"{ctx.user.id}")

        db.hset(
            f"derby:{ctx.guild.id}",
            mapping={
                "swing_count": int(derby["swing_count"]) + 1,
                "total_swing_count": int(derby["total_swing_count"]) + 1,
                "sum_diff": int(derby["sum_diff"]) + diff,
                "total_sum_diff": int(derby["total_sum_diff"]) + diff,
                "hrs": int(derby["hrs"]) + hrs,
                "total_hrs": int(derby["total_hrs"]) + hrs,
            },
        )

        # If user has not swung yet this derby, add them to the hitters list and scoreboard
        if db.sismember(f"derby_hitters:{ctx.guild.id}", f"{ctx.user.id}") == 0:
            db.sadd(f"derby_hitters:{ctx.guild.id}", f"{ctx.user.id}")
            db.hset(
                f"derby_score:{ctx.user.id}",
                mapping={
                    "name": ctx.user.display_name,
                    "swings": 1,
                    "total_diff": diff,
                    "hrs": hrs,
                },
            )
        else:
            score = db.hgetall(f"derby_score:{ctx.user.id}")
            db.hset(
                f"derby_score:{ctx.user.id}",
                mapping={
                    "swings": int(score["swings"]) + 1,
                    "total_diff": int(score["total_diff"]) + diff,
                    "hrs": int(score["hrs"]) + hrs,
                },
            )


def setup(bot: d.Bot):
    bot.add_cog(Derby(bot))
