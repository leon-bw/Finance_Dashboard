"""
Gamification helpers for the learning engine.

Pure functions so the XP/level and streak rules are easy to test and reuse
across routers and seeding.
"""

from datetime import date, timedelta
from typing import Optional

# A lesson is considered passed when at least this fraction of answers are correct.
PASS_THRESHOLD = 0.8

# How much XP is needed to gain a level.
XP_PER_LEVEL = 100


def level_for_xp(xp_total: int) -> int:
    """
    Work out the user's level from their total XP.

    Levels start at 1, and every ``XP_PER_LEVEL`` XP earns a new level.
    """
    if xp_total < 0:
        xp_total = 0
    return xp_total // XP_PER_LEVEL + 1


def xp_to_next_level(xp_total: int) -> int:
    """
    XP remaining until the next level.
    """
    return level_for_xp(xp_total) * XP_PER_LEVEL - xp_total


def calculate_streak(
    last_activity_date: Optional[date],
    current_streak: int,
    today: Optional[date] = None,
) -> int:
    """
    Work out the new streak length given the last day the user was active.

    - No prior activity -> streak starts at 1.
    - Already active today -> streak unchanged (minimum of 1).
    - Active yesterday -> streak increments.
    - A gap of more than a day -> streak resets to 1.
    """
    today = today or date.today()

    if last_activity_date is None:
        return 1
    if last_activity_date == today:
        return current_streak if current_streak > 0 else 1
    if last_activity_date == today - timedelta(days=1):
        return current_streak + 1
    return 1
