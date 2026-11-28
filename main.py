from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from pydantic import ValidationError

from .engine.dice import dice_parse, dice_tool
from .model.model_dice import DiceResult


def _format_roll(expression: str, result: DiceResult) -> str:
    """Format a roll result as a readable calculation expression."""
    if result.kept != result.rolls:
        rolls = ", ".join(str(r) for r in result.rolls)
        terms = f"[{rolls}] → " + " + ".join(str(r) for r in result.kept)
    else:
        terms = " + ".join(str(r) for r in result.kept)

    if result.modifier > 0:
        terms += f" + {result.modifier}"
    elif result.modifier < 0:
        terms += f" - {-result.modifier}"

    return f"{expression}: {terms} = {result.result}"


@register("DND_LLM", "SakiyaYue", "一个简单的 Hello World 插件", "0.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """Optional async plugin initialization method, called automatically after the plugin class is instantiated."""

    # Command registration decorator. The command name is helloworld. Once registered, sending `/helloworld` triggers this command and replies `Hello, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """This is a hello world command""" # Description of this handler, parsed to help users understand the plugin. Recommended to fill in.
        user_name = event.get_sender_name()
        message_str = event.message_str # The plain-text message string sent by the user
        message_chain = event.get_messages() # The message chain of the messages sent by the user # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # Send a plain-text message

    # Roll dice with a DND-style expression, e.g. `/roll 2d6kh1+3`
    @filter.command("roll")
    async def roll(self, event: AstrMessageEvent, dice: str):
        """Roll dice and reply with the calculation expression."""
        try:
            result = dice_tool(dice_parse(dice))
        except ValidationError as e:
            message = "; ".join(
                err["msg"].removeprefix("Value error, ") for err in e.errors()
            )
            yield event.plain_result(f"投掷失败: {message}，示例: /roll 2d6+3")
            return
        except ValueError as e:
            yield event.plain_result(f"投掷失败: {e}，示例: /roll 2d6+3")
            return
        yield event.plain_result(_format_roll(dice, result))

    async def terminate(self):
        """Optional async plugin teardown method, called when the plugin is unloaded or disabled."""
