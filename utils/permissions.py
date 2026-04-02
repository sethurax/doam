import discord as d


def has_doam_permission(member: d.Member, settings: dict, bot: d.Bot):
    if member.id == bot.owner_id:
        return True
    if settings["admin_role"]:
        if member.get_role(int(settings["admin_role"])):
            return True
        else:
            return False
    else:
        return True
