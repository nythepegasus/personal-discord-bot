import os
import sys
import json
import traceback
import discord
import zipfile
from discord.ext import commands

if not os.path.isdir("logs"):
    os.mkdir("logs")

if not os.path.isdir("conf_files"):
    with zipfile.ZipFile("all_backend.zip", "r") as zip_ref:
        for item in zip_ref.namelist():
            if "conf_files" in item:
                zip_ref.extract(item)

if not os.path.isdir("db_files"):
    with zipfile.ZipFile("all_backend.zip", "r") as zip_ref:
        for item in zip_ref.namelist():
            if "db_files" in item:
                zip_ref.extract(item)

if os.path.isfile("conf_files/conf.json"):
    conf_data = json.load(open("conf_files/conf.json"))
    if conf_data["TOKEN"] == "" or conf_data["command_prefix"] == "" or conf_data["owner_id"] == "":
        print("You need to set up conf.json!")
        confirm = input("Do you want to setup conf.json right now? (Y/N): ")
        if confirm.lower() == "y":
            conf_data["TOKEN"] = input("Input Discord bot TOKEN: ")
            conf_data["command_prefix"] = input("Input command prefix: ")
            conf_data["owner_id"] = input("Input owner_id: ")
            json.dump(conf_data, open("conf_files/conf.json", "w"), indent=4)
            print("conf.json filled out, everything should work now!\n(As long as you filled in the correct info)")
        elif confirm.lower() == "n":
            print("Make sure to go through and set up conf.json!\nOtherwise, the bot will not work.")
            exit(1)
        else:
            print("Make sure to go through and set up conf.json!\nOtherwise, the bot will not work.")
            exit(1)

# These should come from a conf file, the TOKEN, command_prefix, and owner_id (and others if need be)
TOKEN = conf_data["TOKEN"]
client = commands.Bot(command_prefix=conf_data["command_prefix"])
client.owner_id = int(conf_data["owner_id"])
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
    funny_activity = discord.Game(name="with my 3 inch thick yogurt slinger")  # This could be in the conf file as well
    await client.change_presence(activity=funny_activity)
    for guild in client.guilds:
        print(f"Tester in {guild}")

client.run(TOKEN)
