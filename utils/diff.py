def calculate_diff(pitch: int, swing: int) -> int:
    """Calculates the difference between the pitch and the swing, accounting for the fact that numbers wrap from 1000 to 1. The minimum result is 0, the maximum result is 500."""
    result = abs(swing - pitch)
    if result > 500:
        if swing > 500:
            return abs(1000 - swing + pitch)
        else:
            return abs(1000 - pitch + swing)
    return result
