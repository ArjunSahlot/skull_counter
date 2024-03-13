import os

import discord
from discord.commands import Option
from dotenv import load_dotenv

load_dotenv()

ACCEPTING_CHARS = "💀🪑"

class ChannelNotSetError(Exception):
    pass


class Log:
    def __init__(self):
        self.log = []
        self.channel_id = None

    def check(self, message):
        if self.channel_id is None:
            raise ChannelNotSetError
        return self.channel_id == message.channel.id

    def add(self, message):
        self.log.append(message)
        print(f"Added message to log: {message.content}")

    def clear(self):
        self.log = []

    def set_channel(self, channel_id):
        self.channel_id = channel_id

    def __repr__(self):
        return "\n".join([message.content for message in self.log])


def on_ready_wrapper(bot):
    async def on_ready():
        print(f"{bot.user.name} is ready")

    return on_ready


async def on_guild_join(guild):
    print(f"\n\n\n\nJoined '{guild.name}'\n\n\n\n")


async def on_guild_remove(guild):
    print(f"\n\n\n\nKicked out of '{guild.name}'\n\n\n\n")


async def on_message(message):
    if LOG.check(message):
        print(f"Logged message from {message.author.name}")
        print(f"Content: {message.content}")
    else:
        print(f"Message from {message.author.name} not logged")
        print(f"Content: {message.content}")


async def log(
    ctx,
    count: Option(int, "Number of lines to show", required=False),
    from_: Option(str, "Time to start from", required=False),
    user: Option(str, "User to show logs for", required=False),
):
    if from_ is not None:
        if user is not None:
            pass
        await ctx.respond(f"from_ is {from_}")
    elif count is not None:
        if user is not None:
            pass
        await ctx.respond(f"count is {count}")
    elif user is not None:
        await ctx.respond(f"user is {user}")
    else:
        if str(LOG) == "":
            await ctx.respond("No logs")
        else:
            await ctx.respond(str(LOG))


async def start_monitoring(ctx):
    await ctx.response.defer()
    LOG.clear()
    print(ctx.channel_id)
    LOG.set_channel(ctx.channel_id)

    async for message in ctx.channel.history(limit=None):
        await on_message(message)

    await ctx.followup.send(f"Started monitoring {ctx.channel.name}")


async def help(ctx):
    await ctx.respond(
"""
Commands:
- /help: Get help with the bot
- /log: Check the log

/help: Get help with the bot

/log: Check the log
/log [count]: Check the last [count] lines of the log
/log [from]: Check the log from [from] to now
/log [user]: Check the log for [user]
""")


if __name__ == "__main__":
    from deployment import start_server

    start_server()
    print("Server started on port 8000")

    intents = discord.Intents.default()
    intents.messages = True
    bot = discord.Bot(intents=intents)

    LOG = Log()

    bot.event(on_ready_wrapper(bot))
    bot.event(on_guild_join)
    bot.event(on_guild_remove)
    bot.event(on_message)

    bot.slash_command(name="help", description="Get help with the bot")(help)
    bot.slash_command(name="log", description="Check the log")(log)
    bot.slash_command(
        name="startmonitoring", description="Start monitoring the channel"
    )(start_monitoring)

    bot.run(os.getenv("DISCORD_TOKEN"))

