import asyncio

from telegram_ai_assistant.telegram_adapter import COMMAND_MENU, register_commands


class FakeCommand:
    def __init__(self, command, description):
        self.command = command
        self.description = description


class FakeBot:
    def __init__(self):
        self.commands = None

    async def set_my_commands(self, commands):
        self.commands = commands


def test_register_commands_sets_russian_menu_without_secrets():
    bot = FakeBot()
    asyncio.run(register_commands(bot, FakeCommand))
    assert [(item.command, item.description) for item in bot.commands] == list(COMMAND_MENU)
    assert all("TOKEN" not in item.description.upper() for item in bot.commands)
    assert all("KEY" not in item.description.upper() for item in bot.commands)
