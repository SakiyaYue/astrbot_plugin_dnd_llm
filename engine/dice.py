import random
import re
from typing import Literal, cast

from ..model.model_dice import DiceInput, DiceResult

DICE_PATTERN = re.compile(
    r"^(?P<count>[1-9]\d*)"
    r"d"
    r"(?P<sides>[1-9]\d*)"
    r"(?:(?P<keep>kh|kl)(?P<keep_count>[1-9]\d*))?"
    r"(?:(?P<sign>[+-])(?P<modifier>\d+))?$"
)


def dice_roll(count: int, sides: int) -> list[int]:
    """Roll specified number of dice with sides sides and return the result."""
    result = [random.randint(1, sides) for _ in range(count)]
    return result


def dice_parse(dice_str: str) -> DiceInput:
    """Parse a dice command string into structured parameters."""
    m = DICE_PATTERN.match(dice_str.strip())
    if not m:
        raise ValueError(f"无效的骰子表达式: {dice_str}")

    modifier = int(m.group("modifier") or 0)
    if m.group("sign") == "-":
        modifier = -modifier

    return DiceInput(
        count=int(m.group("count")),
        sides=int(m.group("sides")),
        keep=cast(Literal["kh", "kl"] | None, m.group("keep")),
        keep_count=int(m.group("keep_count")) if m.group("keep_count") else None,
        modifier=modifier,
    )


def dice_tool(data: DiceInput | dict) -> DiceResult:
    """Roll dice from structured parameters and return results."""
    payload = DiceInput.model_validate(data)  # if data is a dict, convert to DiceInput

    rolls = dice_roll(payload.count, payload.sides)

    kept = rolls
    if payload.keep == "kh":
        kept = sorted(rolls, reverse=True)[: payload.keep_count]
    elif payload.keep == "kl":
        kept = sorted(rolls)[: payload.keep_count]

    return DiceResult(
        rolls=rolls,
        kept=kept,
        modifier=payload.modifier,
        result=sum(kept) + payload.modifier,
    )
