from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

ALLOWED_SIDES = {4, 6, 8, 10, 12, 20, 100}


class DiceInput(BaseModel):
    """Structured parameters of a dice expression."""

    count: int
    sides: int
    keep: Literal["kh", "kl"] | None = None
    keep_count: int | None = None
    modifier: int = 0

    @field_validator("count")
    @classmethod
    def check_count(cls, value: int) -> int:
        if value < 1:
            raise ValueError("投掷数量不能小于 1")
        if value > 100:
            raise ValueError("单次投掷骰子数量不能超过 100")
        return value

    @field_validator("sides")
    @classmethod
    def check_sides(cls, value: int) -> int:
        if value not in ALLOWED_SIDES:
            raise ValueError("不支持的骰子面数")
        return value

    @model_validator(mode="after")
    def check_keep(self) -> "DiceInput":
        if self.keep is None:
            return self
        if self.keep_count is None:
            raise ValueError("指定保留方式时必须设置保留数量")
        if self.keep_count < 1:
            raise ValueError("保留数量不能小于 1")
        if self.keep_count > self.count:
            raise ValueError("保留数量不能超过投掷数量")
        return self


class DiceResult(BaseModel):
    """Roll result returned by dice_tool."""

    rolls: list[int]
    kept: list[int]
    modifier: int
    result: int
