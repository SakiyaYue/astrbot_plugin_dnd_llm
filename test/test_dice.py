import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from astrbot_plugin_dnd_llm.engine.dice import dice_parse, dice_roll, dice_tool
from astrbot_plugin_dnd_llm.model.model_dice import DiceInput

# ---------- dice_roll ----------


def test_dice_roll_count_and_range():
    rolls = dice_roll(5, 6)
    assert len(rolls) == 5
    assert all(1 <= r <= 6 for r in rolls)


def test_dice_roll_single_die():
    rolls = dice_roll(1, 20)
    assert len(rolls) == 1
    assert 1 <= rolls[0] <= 20


# ---------- dice_parse ----------


def test_dice_parse_plain():
    data = dice_parse("2d6")
    assert data.model_dump() == {
        "count": 2,
        "sides": 6,
        "keep": None,
        "keep_count": None,
        "modifier": 0,
    }


def test_dice_parse_positive_modifier():
    data = dice_parse("4d8+3")
    assert data.count == 4
    assert data.sides == 8
    assert data.modifier == 3


def test_dice_parse_negative_modifier():
    data = dice_parse("1d20-5")
    assert data.modifier == -5


def test_dice_parse_keep_high():
    data = dice_parse("4d6kh3")
    assert data.keep == "kh"
    assert data.keep_count == 3


def test_dice_parse_keep_low_with_modifier():
    data = dice_parse("5d10kl2+1")
    assert data.keep == "kl"
    assert data.keep_count == 2
    assert data.modifier == 1


def test_dice_parse_strips_whitespace():
    data = dice_parse("  3d12  ")
    assert data.count == 3
    assert data.sides == 12


@pytest.mark.parametrize(
    "bad",
    ["", "d20", "2d", "0d6", "2d0", "2d6+", "2d6kh", "2d6kh0", "abc", "2d6*2", "1d7"],
)
def test_dice_parse_invalid(bad):
    with pytest.raises(ValueError):
        dice_parse(bad)


# ---------- DiceInput ----------


def _data(**kwargs):
    base = {"count": 1, "sides": 6, "keep": None, "keep_count": None, "modifier": 0}
    base.update(kwargs)
    return base


def test_dice_input_ok():
    data = DiceInput(**_data(count=4, sides=20, keep="kh", keep_count=3))
    assert data.keep_count == 3


def test_dice_input_too_many():
    with pytest.raises(ValueError):
        DiceInput(**_data(count=101))


def test_dice_input_unsupported_sides():
    with pytest.raises(ValueError):
        DiceInput(**_data(sides=7))


def test_dice_input_keep_count_exceeds_count():
    with pytest.raises(ValueError):
        DiceInput(**_data(count=2, keep="kh", keep_count=3))


def test_dice_input_keep_without_keep_count():
    with pytest.raises(ValueError):
        DiceInput(**_data(count=2, keep="kl"))


# ---------- dice_tool ----------


def test_dice_tool_plain_result(monkeypatch):
    monkeypatch.setattr("astrbot_plugin_dnd_llm.engine.dice.dice_roll", lambda count, sides: [3, 5])
    out = dice_tool(_data(count=2, sides=6))
    assert out.rolls == [3, 5]
    assert out.kept == [3, 5]
    assert out.modifier == 0
    assert out.result == 8


def test_dice_tool_modifier(monkeypatch):
    monkeypatch.setattr("astrbot_plugin_dnd_llm.engine.dice.dice_roll", lambda count, sides: [10])
    out = dice_tool(_data(count=1, sides=20, modifier=-2))
    assert out.result == 8


def test_dice_tool_keep_high(monkeypatch):
    monkeypatch.setattr("astrbot_plugin_dnd_llm.engine.dice.dice_roll", lambda count, sides: [2, 6, 4])
    out = dice_tool(_data(count=3, sides=6, keep="kh", keep_count=2))
    assert out.rolls == [2, 6, 4]
    assert out.kept == [6, 4]
    assert out.result == 10


def test_dice_tool_keep_low(monkeypatch):
    monkeypatch.setattr("astrbot_plugin_dnd_llm.engine.dice.dice_roll", lambda count, sides: [2, 6, 4])
    out = dice_tool(_data(count=3, sides=6, keep="kl", keep_count=1, modifier=1))
    assert out.kept == [2]
    assert out.result == 3


def test_dice_tool_rejects_invalid():
    with pytest.raises(ValueError):
        dice_tool(_data(sides=5))
