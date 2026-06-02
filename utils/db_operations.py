import discord as d
from db import db


def fetch_server_settings(guild_id: int):
    return db.hgetall(f"settings:{guild_id}")


def fetch_active_doam(guild_id: int):
    return db.hgetall(f"doam:{guild_id}")


def fetch_active_derby(guild_id: int):
    return db.hgetall(f"derby:{guild_id}")


def fetch_hitting_logs(ctx: d.ApplicationContext):
    if ctx.guild:
        return db.lrange(f"p1_hitting:{ctx.guild.id}", 0, -1), db.lrange(
            f"p2_hitting:{ctx.guild.id}", 0, -1
        )


def set_pitch(ctx: d.ApplicationContext, pitch: int):
    if ctx.guild:
        db.hset(f"doam:{ctx.guild.id}", mapping={"pitch": pitch})


def set_derby_pitch(ctx: d.ApplicationContext, pitch: int):
    if ctx.guild:
        db.hset(f"derby:{ctx.guild.id}", mapping={"pitch": pitch})


def delete_doam_data(ctx: d.ApplicationContext):
    if ctx.guild:
        db.delete(f"doam:{ctx.guild.id}")
        db.delete(f"p1_hitting:{ctx.guild.id}")
        db.delete(f"p2_hitting:{ctx.guild.id}")


def delete_derby_data(ctx: d.ApplicationContext):
    if ctx.guild:
        db.delete(f"derby:{ctx.guild.id}")
        db.delete(f"derby_results:{ctx.guild.id}")
        db.delete(f"derby_hitters:{ctx.guild.id}")
        db.delete(f"derby_scoreboard:{ctx.guild.id}")


def register_doam(ctx: d.ApplicationContext, player1: d.Member, player2: d.Member):
    if ctx.guild:
        db.hset(
            f"doam:{ctx.guild.id}",
            mapping={
                "player1": player1.id,
                "player2": player2.id,
                "p1_name": player1.display_name,
                "p2_name": player2.display_name,
                "p1_avatar": player1.display_avatar.url,
                "p2_avatar": player2.display_avatar.url,
                "p1_score": 0,
                "p2_score": 0,
                "round": 1,
                "pitching": player1.id,
                "hitting": player2.id,
                "pitch": 0,
            },
        )

        db.lpush(
            f"p1_hitting:{ctx.guild.id}",
            "-",
            "-----------------------------",
            "Pitch | Swing | Diff | Result",
            "-----------------------------",
        )
        db.lpush(
            f"p2_hitting:{ctx.guild.id}",
            "-",
            "-----------------------------",
            "Pitch | Swing | Diff | Result",
            "-----------------------------",
        )


def register_derby(ctx: d.ApplicationContext, pitcher: d.Member, pitches: int):
    if ctx.guild:
        db.hset(
            f"derby:{ctx.guild.id}",
            mapping={
                "pitcher": pitcher.id,
                "pitcher_name": pitcher.display_name,
                "pitcher_avatar": pitcher.display_avatar.url,
                "total_pitches": pitches,
                "round": 1,
                "pitch": 0,
                "pitch_allowed": "yes",
                "swing_allowed": "yes",
                "swing_count": 0,
                "sum_diff": 0,
                "hrs": 0,
                "total_swing_count": 0,
                "total_sum_diff": 0,
                "total_hrs": 0,
            },
        )

        db.lpush(
            f"derby_results:{ctx.guild.id}",
            "-",
            "-----------------------------",
            "Rd   |  P  | #Sw | Dif | HRs ",
            "-----------------------------",
        )


def set_server_settings(
    ctx: d.ApplicationContext,
    channel: d.abc.GuildChannel | None = None,
    derby_channel: d.TextChannel | None = None,
    admin_role: d.Role | None = None,
    ping_role: d.Role | None = None,
):
    if ctx.guild:
        db.hset(
            f"settings:{ctx.guild.id}",
            mapping={
                "channel": channel.id if channel else "",
                "derby_channel": derby_channel.id if derby_channel else "",
                "admin_role": admin_role.id if admin_role else "",
                "ping_role": ping_role.id if ping_role else "",
            },
        )

        # Since I want to show the updated settings, I'll fetch them again here rather than requiring another function call in the parent
        return fetch_server_settings(ctx.guild.id)
