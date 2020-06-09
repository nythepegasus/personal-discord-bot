import sys
import traceback
import discord
from discord.ext import commands

TOKEN = "NTIxNTUwNzIyMzU0MTE4NjY2.Xs6qQQ.Ngcld6mD4Ip6CzkCz_mjLu8Nf-E"
client = commands.Bot(command_prefix="buh!")
client.owner_id = 195864152856723456
client.remove_command("help")

initial_extensions = [
            "modules.admin",
            "modules.points",
            "modules.phrases",
            "modules.util"
]

for extension in initial_extensions:
    try:
        client.load_extension(extension)
        print(f"Loaded {extension}.")
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        print(f"{type(e).__name__} - {e}")
        traceback.print_exc()


@client.event
async def on_ready():
    funny_activity = discord.Game(name="with my 3 inch thick yogurt slinger")
    await client.change_presence(activity=funny_activity)
    for guild in client.guilds:
        print(f"Tester in {guild}")

client.run(TOKEN)
