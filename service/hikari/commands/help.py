import lightbulb

from service.hikari.hikari_bot import loader


@loader.command
class Help(
        lightbulb.SlashCommand,
        name="help",
        description="Show help message"):
    @lightbulb.invoke
    async def invoke(self, context: lightbulb.Context) -> None:
        await context.respond("Help message goes here")
