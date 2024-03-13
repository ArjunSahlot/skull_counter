import os

import discord
from discord.commands import Option
from dotenv import load_dotenv

load_dotenv()

ACCEPTING_CHARS = ("💀", "🪑")


class ChannelNotSetError(Exception):
    pass


class Log:
    def __init__(self):
        self.log = []
        self.last = None
        self.channel_id = None

    def add(self, message):
        self.log.append(message)
        self.last = message
        print(f"Added message to log: {message.content}")

    def pop(self):
        self.log.pop()

    def clear(self):
        self.log = []
        self.last = None

    def set_channel(self, channel_id):
        self.channel_id = channel_id

    def flip(self):
        self.log = list(reversed(self.log))

    def query_counts(self, count):
        counts = {}

        for message in self.log:
            if message.author not in counts:
                counts[message.author] = 0
            counts[message.author] += 1

        return counts
    
    def query_user(self, user):
        return [message for message in self.log if message.author == user]

    def query_count(self, count):
        return self.log[-count:]

    def __repr__(self):
        return "\n".join([message.content for message in self.log])


async def on_ready():
    print(f"{bot.user.name} is ready")


async def on_guild_join(guild):
    print(f"\n\n\n\nJoined '{guild.name}'\n\n\n\n")


async def on_guild_remove(guild):
    print(f"\n\n\n\nKicked out of '{guild.name}'\n\n\n\n")


async def on_message(message):
    if message.channel.id == LOG.channel_id:
        if (message.content not in ACCEPTING_CHARS) or (
            LOG.log and message.author == LOG.log[-1].author
        ):
            try:
                await message.delete()
            except discord.errors.NotFound:
                print("Message not found")
        else:
            LOG.add(message)


async def log(
    ctx,
    count: Option(int, "Number of lines to show", default=10, required=True),
    user: Option(discord.User, "User to show logs for", required=False),
):
    await ctx.response.defer()

    logs = []
    if user is not None:
        logs = LOG.query_user(user)[-count:]
    else:
        logs = LOG.query_count(count)

    # char limit: 2000
    strings = []
    curr = ""
    for log in logs:
        curr

    for string in strings:
        await ctx.followup.send(string)


async def start_monitoring(ctx):
    await ctx.response.defer()
    LOG.clear()
    LOG.set_channel(ctx.channel_id)

    last = None

    async for message in ctx.channel.history(limit=None):
        if message.content not in ACCEPTING_CHARS:
            try:
                await message.delete()
            except discord.errors.NotFound:
                print("Message not found")
            continue

        if last is not None and message.author == last.author:
            try:
                await last.delete()
                LOG.pop()
            except discord.errors.NotFound:
                print("Message not found")

        LOG.add(message)
        last = message

    LOG.flip()

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
"""
    )


if __name__ == "__main__":
    from deployment import start_server

    start_server()
    print("Server started on port 8000")

    intents = discord.Intents.default()
    intents.messages = True
    bot = discord.Bot(intents=intents)

    LOG = Log()

    bot.event(on_ready)
    bot.event(on_guild_join)
    bot.event(on_guild_remove)
    bot.event(on_message)

    bot.slash_command(name="help", description="Get help with the bot")(help)
    bot.slash_command(name="log", description="Check the log")(log)
    bot.slash_command(
        name="startmonitoring", description="Start monitoring the channel"
    )(start_monitoring)

    bot.run(os.getenv("DISCORD_TOKEN"))
