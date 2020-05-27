import sys, traceback, discord
from discord.ext import commands


"""
Start of the variables and such for the backend.
"""


TOKEN = "NzA2NTYzMzI0NTYwODAxNzkz.Xs54kw.En9cwKk5jTpIAOH1LjX32_VuvR0"
client = commands.Bot(command_prefix="buh!")
client.remove_command("help")

initial_extensions = [
            "modules.admin",
            "modules.points",
            "modules.phrases",
            "modules.util"
]


"""
Start of importing cogs.
"""


for extension in initial_extensions:
    try:
        client.load_extension(extension)
        print(f"Loaded {extension}.")
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()


"""
Starting the events, such as messages and pins.
"""


@client.event
async def on_ready():
    funny_activity = discord.Game(name="with my 3 inch thick yogurt slinger")
    await client.change_presence(activity=funny_activity)
    for guild in client.guilds:
        print(f"Tester in {guild}")


client.run(TOKEN)
