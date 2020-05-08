import os, json, datetime, time, psutil, discord
from discord.ext import commands

words_to_track_file = "phrases.json"

if not os.path.isfile(words_to_track_file):
    with open(words_to_track_file, "w") as f:
        f.write('{\n"phrases": [],\n"houses": [\n{\n"house_name": "Gryffindor",\n"house_points": 0\n},\n{\n"house_name": "Slytherin",\n"house_points": 0\n},\n{\n"house_name": "Ravenclaw",\n"house_points": 0\n},\n{\n"house_name": "Hufflepuff",\n"house_points": 0\n}\n],\n"last_pin_count": 0\n}')


tonys_a_cunt = [
        "\u0628",
        "\u064d",
        "\u0631",
        "nigga",
        "nigger",
]

TOKEN = "NTIxNTUwNzIyMzU0MTE4NjY2.XqzV7Q.gvob9l9tcZe2_W_vH_54Y-shW1A"
client = discord.Client()
bot = commands.Bot(command_prefix="buh!")


@bot.command(aliases=["ap"])
async def add_phrase(ctx, phrase):
    data = json.load(open(words_to_track_file))
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
            return "You're a cunt!"
    add_phrase = {
        "uid": cur_index,
        "phrase": phrase,
        "times_said": 0,
    }
    with open(words_to_track_file, "w") as f:
        data["phrases"].append(add_phrase)
        f.write(json.dumps(data, indent=4))
        await ctx.send("Phrase added!")


def update_phrase(phrase):
    data = json.load(open(words_to_track_file))
    for d in data["phrases"]:
        if d.get("phrase").lower() in phrase.lower():
            d["times_said"] += 1
    with open(words_to_track_file, "w") as f:
        f.write(json.dumps(data, indent=4))
        return "Updated phrase!"

@bot.command(aliases=["rp"])
async def remove_phrase(ctx, phrase):
    data = json.load(open(words_to_track_file))
    with open(words_to_track_file, "w") as f:
        data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
        f.write(json.dumps(data, indent=4))
        await ctx.send("Removed phrase!")

@bot.command(aliases=["arcp"])
async def archive_pins(ctx):
    for guild in client.guilds:
        if guild.name == "Trolls Stan Club":
            main_guild = guild
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


@bot.command(aliases=["hp"])
async def house_points(ctx):
    data = json.load(open(words_to_track_file))
    house_emb = discord.Embed(title="House points", colour=0x00adff)
    for house in data["houses"]:
        house_emb.add_field(name=house["house_name"], value=house["house_points"], inline=False)
    await ctx.send(embed=house_emb)

@bot.command(aliases=["pc"])
async def phrase_counts(ctx):
    data = json.load(open(words_to_track_file))
    string_to_print = ""
    for phrase in data["phrases"]:
        string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
    await ctx.send(string_to_print)

@client.event
async def on_ready():
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
    if "buh!help" in message.content:
        help_emb = discord.Embed(title="Bot Commands", colour=0x00adff)
        help_emb.add_field(name="buh!add_phrase | buh!ap", value="Add phrase to the tracker", inline=False)
        help_emb.add_field(name="buh!remove_phrase | buh!rp", value="Remove phrase from the tracker", inline=False)
        help_emb.add_field(name="buh!phrases_counts | buh!pc", value="Check phrases on the tracker", inline=False)
        help_emb.add_field(name="buh!archive_pins | buh!arcp", value="Archive all pins from #general chat", inline=False)
        help_emb.add_field(name="buh!house_points | buh!hp", value="Check each house's points.", inline=False)
        help_emb.add_field(name="More to come!", value=":3", inline=False)
        help_emb.set_footer(text="Developed by Nikki")
        await message.channel.send(embed=help_emb)
        return
    update_phrase(message.content)

@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    if channel.name != "general":
        return
    data = json.load(open(words_to_track_file))
    myPins = await channel.pins()
    if data["last_pin_count"] > len(myPins):
        data["last_pin_count"] = len(myPins)
        with open(words_to_track_file, "w") as f:
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
            with open(words_to_track_file, "w") as f:
                f.write(json.dumps(data, indent=4))
            await channel.send(f"10 points to {da_house}!")
        except IndexError:
            pass

client.run(TOKEN)
