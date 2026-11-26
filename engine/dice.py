import random
import re

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


def dice_parse(dice_str: str) -> dict:
    """Parse a dice command string into structured parameters."""
    m = DICE_PATTERN.match(dice_str.strip())
    if not m:
        raise ValueError(f"无效的骰子表达式: {dice_str}")

    modifier = int(m.group("modifier") or 0)
    if m.group("sign") == "-":
        modifier = -modifier

    return {
        "count": int(m.group("count")),
        "sides": int(m.group("sides")),
        "keep": m.group("keep"),
        "keep_count": int(m.group("keep_count")) if m.group("keep_count") else None,
        "modifier": modifier,
    }


def validate_dice(data: dict) -> None:
    count = int(data["count"])
    sides = int(data["sides"])

    if count > 100:
        raise ValueError("单次投掷骰子数量不能超过 100")

    if sides not in {4, 6, 8, 10, 12, 20, 100}:
        raise ValueError("不支持的骰子面数")

    if data["keep"]:
        keep_count = int(data["keep_count"])

        if keep_count > count:
            raise ValueError("保留数量不能超过投掷数量")


def dice_tool(data: dict) -> dict:
    """Roll dice from structured parameters and return results."""
    validate_dice(data)

    count = int(data["count"])
    sides = int(data["sides"])
    keep = data.get("keep")
    keep_count = data.get("keep_count")
    modifier = int(data.get("modifier") or 0)

    rolls = dice_roll(count, sides)

    kept = rolls
    if keep == "kh":
        kept = sorted(rolls, reverse=True)[:keep_count]
    elif keep == "kl":
        kept = sorted(rolls)[:keep_count]

    result = sum(kept) + modifier

    return {
        "rolls": rolls,
        "kept": kept,
        "modifier": modifier,
        "result": result,
    }
