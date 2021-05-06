import sys
import json
import traceback
import discord
import sentry_sdk
import pushover
from discord.ext import commands

# These should come from a conf file, the TOKEN, command_prefix, and owner_id (and others if need be)
conf_data = json.load(open("conf_files/conf.json"))
if conf_data["TOKEN"] == "" or conf_data["command_prefix"] == "" or conf_data["owner_id"] == "":
    print("You need to set up conf.json!")
    exit(1)
TOKEN = conf_data["TOKEN"]

intents = discord.Intents().all()
client = commands.Bot(command_prefix=conf_data["command_prefix"], intents=intents)
client.owner_id = int(conf_data["owner_id"])

psh_data = conf_data['pushover']
if psh_data['user_key'] != "" and psh_data['api_key'] != "":
    client.pshovr = pushover.Client(user_key=psh_data['user_key'],
                                    api_token=psh_data['api_key'])
else:
    client.pshovr = None

client.remove_command("help")

sentry_sdk.init(
    conf_data["sentry_sdk"],
    traces_sample_rate=1.0
)

for extension in conf_data["modules"]:
    try:
        client.load_extension(extension)
        print(f"Loaded {extension}.")
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        print(f"{type(e).__name__} - {e}")
        traceback.print_exc()


@client.before_invoke
async def delete_message(ctx):
    if not isinstance(ctx.channel, discord.channel.DMChannel) and \
       not isinstance(ctx.channel, discord.channel.GroupChannel):
        await ctx.message.delete()


@client.event
async def on_ready():
    funny_activity = discord.Game(name="with my 3 inch thick yogurt slinger")  # This could be in the conf file as well
    await client.change_presence(activity=funny_activity)
    for guild in client.guilds:
        print(f"Tester in {guild}")


@client.event
async def on_message_delete(msg):
    if msg.author == client.user:
        return
    elif "buh!" in msg.content:
        return
    with open("logs/deleted_messages.log", "a") as f:
        f.write(f"[{str(msg.created_at)}] {msg.author.name}: {msg.content}\n")


@client.event
async def on_raw_reaction_add(reaction):
    if str(reaction.emoji.name) == '🗑️':
        channel = await client.fetch_channel(reaction.channel_id)
        msg = await channel.fetch_message(reaction.message_id)
        if msg.author == client.user:
            await msg.delete()

client.run(TOKEN)
