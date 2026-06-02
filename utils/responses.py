from enum import StrEnum


class CommandResponse(StrEnum):
    """Defines a list of common response strings for the success and failure of various commands."""

    NO_SETTINGS = (
        "This server has not been set up for use with DOAM bot. Please run `/settings set` to get started!",
    )

    MISSING_START_PERM = ("You do not have permission to start DOAMs in this server.",)
    MISSING_END_PERM = ("You do not have permission to end DOAMs in this server.",)

    ACTIVE_DOAM = (
        "There is already an active DOAM in this server. Please wait for it to end before starting a new one.",
    )
    NO_ACTIVE_DOAM = (
        "There is no active DOAM in this server. Use `/doam start` to start one!",
    )

    ACTIVE_DERBY = (
        "There is already an active DOAM Run Derby in this server. Please wait for it to end before starting a new one.",
    )
    NO_ACTIVE_DERBY = (
        "There is no active DOAM Run Derby in this server. Use /derby start to start one!",
    )

    DOAM_STARTED = ("DOAM started! Use `/doam end` to end it.",)
    DOAM_ENDED = ("DOAM ended. Use `/doam start` to start a new one!",)

    DERBY_STARTED = ("DOAM Run Derby started! Use `/derby end` to end it.",)
    DERBY_ENDED = ("DOAM Run Derby ended. Use `/derby start` to start a new one!",)

    NOT_PITCHER = ("You are not the current pitcher in this DOAM.",)
    NOT_DERBY_PITCHER = ("You are not the pitcher in the current DOAM Run Derby",)
    NOT_HITTER = ("You are not the current hitter in this DOAM.",)
    NO_SWING_YET = "Please wait for the pitcher to throw before submitting your swing!"
    NO_DERBY_SWING = (
        "It is not time to swing. Watch for a message in the DOAM channel to know when!"
    )
