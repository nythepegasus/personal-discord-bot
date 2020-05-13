import os, json, datetime, time, psutil, discord, speedtest
from discord.ext import commands


"""
Start of the variables and such for the backend.
"""

global net_message_counter

db_file = "phrases.json"


if not os.path.isfile(db_file):
    with open(db_file, "w") as f:
        f.write('{\n"phrases": [],\n"houses": [\n{\n"house_name": "Gryffindor",\n"house_points": 0\n},\n{\n"house_name": "Slytherin",\n"house_points": 0\n},\n{\n"house_name": "Ravenclaw",\n"house_points": 0\n},\n{\n"house_name": "Hufflepuff",\n"house_points": 0\n}\n],\n"last_pin_count": 0\n}')


tonys_a_cunt = [
        "\u0628",
        "\u064d",
        "\u0631",
        "nigga",
        "nigger",
]

TOKEN = "NTIxNTUwNzIyMzU0MTE4NjY2.XqzV7Q.gvob9l9tcZe2_W_vH_54Y-shW1A"
client = commands.Bot(command_prefix="buh!")
client.remove_command("help")


"""
Start of the commands and functions for all the backend.
"""


@client.command(aliases=["h"])
async def help(ctx):
    help_emb = discord.Embed(title="Bot Commands", colour=0x00adff)
    help_emb.add_field(name="buh!add_phrase | buh!ap", value="Add phrase to the tracker", inline=False)
    help_emb.add_field(name="buh!remove_phrase | buh!rp", value="Remove phrase from the tracker", inline=False)
    help_emb.add_field(name="buh!phrases_counts | buh!pc", value="Check phrases on the tracker", inline=False)
    help_emb.add_field(name="buh!archive_pins | buh!arcp", value="Archive all pins from #general chat", inline=False)
    help_emb.add_field(name="buh!house_points | buh!hp", value="Check each house's points.", inline=False)
    help_emb.add_field(name="buh!stats", value="Check the discord bot's current server stats", inline=False)
    help_emb.add_field(name="More to come!", value=":3", inline=False)
    help_emb.set_footer(text="Developed by Nikki")
    await ctx.send(embed=help_emb)


@client.command(name="add_phrase", aliases=["ap"])
async def add_phrase(ctx, phrase):
    data = json.load(open(db_file))
    try:
        cur_index = data["phrases"][-1]["uid"] + 1
    except IndexError:
        cur_index = 1
    for line in data["phrases"]:
        if phrase == line["phrase"]:
            return "Phrase already exists!"
        elif len(phrase) <= 2:
            return "Phrase too short!"
        elif len(phrase) >= 35:
            return "Phrase too long!"
        elif any(bad in phrase for bad in tonys_a_cunt):
            await ctx.send("You're a cunt!")
    add_phrase = {
        "uid": cur_index,
        "phrase": phrase,
        "times_said": 0,
    }
    with open(db_file, "w") as f:
        data["phrases"].append(add_phrase)
        f.write(json.dumps(data, indent=4))
        await ctx.send("Phrase added!")


def update_phrase(phrase):
    data = json.load(open(db_file))
    for d in data["phrases"]:
        if d.get("phrase").lower() in phrase.lower():
            d["times_said"] += 1
    with open(db_file, "w") as f:
        f.write(json.dumps(data, indent=4))
        return "Updated phrase!"


@client.command(name="remove_phrase", aliases=["rp"])
async def remove_phrase(ctx, phrase):
    data = json.load(open(db_file))
    with open(db_file, "w") as f:
        data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
        f.write(json.dumps(data, indent=4))
        await ctx.send("Removed phrase!")


@client.command(name="archive_pins", aliases=["arcp"])
async def archive_pins(ctx):
    guild = client.guilds[0]
    for channel in main_guild.channels:
        if channel.name == "general":
            general_chat = channel
    for channel in main_guild.channels:
        if channel.name == "archived-pins":
            archive_channel = channel
    myPins = await general_chat.pins()
    if len(myPins) == 0:
        await ctx.send("No more pins")
    for pin in myPins:
        emb = discord.Embed(
            description = pin.content,
            timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
        )
        emb.set_author(
            name=pin.author,
            icon_url=pin.author.avatar_url,
            url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                pin.guild.id, pin.channel.id, pin.id)
        )
        if pin.attachments:
            if len(pin.attachments) > 1:
                img_url = pin.attachments[0].url
                emb.set_image(url=img_url)
                emb.set_footer(text=f"Part 1 | Archived from #{pin.channel}")
                await archive_channel.send(embed=emb)
                attach_counter = 1
                try:
                    for attachment in pin.attachments:
                        next_emb = discord.Embed(
                            timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
                        )
                        next_emb.set_author(
                        name=pin.author,
                        icon_url=pin.author.avatar_url,
                        url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                            pin.guild.id, pin.channel.id, pin.id)
                        )
                        img_url = pin.attachments[attach_counter].url
                        next_emb.set_image(url=img_url)
                        next_emb.set_footer(text=f"Part {attach_counter+1} | Archived from #{pin.channel}")
                        attach_counter += 1
                        await archive_channel.send(embed=next_emb)
                except IndexError:
                    pass
            elif len(pin.attachments) == 1:
                img_url = pin.attachments[0].url
                emb.set_image(url=img_url)
                emb.set_footer(text=f"Archived from #{pin.channel}")
                await archive_channel.send(embed=emb)
        else:
            await archive_channel.send(embed=emb)
        await pin.unpin()
    await ctx.send(f"Archived the pins! Check them out in #{archive_channel}!")


@client.command(name="house_points", aliases=["hp"])
async def house_points(ctx):
    data = json.load(open(db_file))
    house_emb = discord.Embed(title="House points", colour=0x00adff)
    for house in data["houses"]:
        house_emb.add_field(name=house["house_name"], value=house["house_points"], inline=False)
    await ctx.send(embed=house_emb)


@client.command(name="phrase_counts", aliases=["pc"])
async def phrase_counts(ctx):
    data = json.load(open(db_file))
    string_to_print = ""
    for phrase in data["phrases"]:
        string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
    await ctx.send(string_to_print)


@client.command()
async def stats(ctx):
    stat_emb = discord.Embed(title="Discord Bot's Server Stats", colour=0x00adff)
    stat_emb.add_field(name="Current Uptime", value=time.strftime("%H:%M:%S", time.gmtime(int(float(open('/proc/uptime').readline().split()[0])))))
    stat_emb.add_field(name="RAM Percentage", value=psutil.virtual_memory()[2])
    stat_emb.add_field(name="CPU Percentage", value=psutil.cpu_percent())
    await ctx.send(embed=stat_emb)


@client.command()
async def netstats(ctx):
    global net_message_counter
    if net_message_counter >= 20:
        net_message_counter = 0
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download(threads=4)
        s.upload(threads=4)
        url = s.results.share()
        net_emb = discord.Embed(title="Discord Bot's Network Speeds", colour=0x00adff)
        net_emb.set_image(url=url)
        await ctx.send(embed=net_emb)
    else:
        await ctx.send("Look man, I can't keep running that over and over again.")


"""
Starting the events, such as messages and pins.
"""


@client.event
async def on_ready():
    global net_message_counter
    net_message_counter = 20
    funny_activity = discord.Game(name="with my 3 inch thick yogurt slinger")
    await client.change_presence(activity=funny_activity)
    for guild in client.guilds:
        print(f"Tester in {guild}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if any(bad in message.content for bad in tonys_a_cunt):
        await message.delete()
        dmchannel = await message.author.create_dm()
        await dmchannel.send("You're a cunt for trying that.")
    global net_message_counter
    net_message_counter += 1
    update_phrase(message.content)
    await client.process_commands(message)


@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    if channel.name != "general":
        return
    data = json.load(open(db_file))
    myPins = await channel.pins()
    if data["last_pin_count"] > len(myPins):
        data["last_pin_count"] = len(myPins)
        with open(db_file, "w") as f:
            f.write(json.dumps(data, indent=4))
        return
    else:
        data["last_pin_count"] = len(myPins)
        try:
            latestPin = myPins[0]
            for house in data["houses"]:
                if house["house_name"].lower() in [y.name.lower() for y in latestPin.author.roles]:
                    da_house = house["house_name"]
                    house["house_points"] += 10
                else:
                    pass
            with open(db_file, "w") as f:
                f.write(json.dumps(data, indent=4))
            await channel.send(f"10 points to {da_house}!")
        except IndexError:
            pass


client.run(TOKEN)
