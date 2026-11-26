from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

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

    async def terminate(self):
        """Optional async plugin teardown method, called when the plugin is unloaded or disabled."""
