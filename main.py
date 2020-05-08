import os, json, datetime, time, psutil, discord


words_to_track_file = "phrases.json"

tonys_a_cunt = [
        "\u0628",
        "\u064d",
        "\u0631",
]

def add_phrase(phrase):
    data = json.load(open(words_to_track_file))
    try:
        cur_index = data["phrases"][-1]["uid"] + 1
    except IndexError:
        cur_index = 1
    for line in data["phrases"]:
        if phrase == line["phrase"]:
            return "Phrase already exists!"
        elif len(phrase) <= 3:
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
        return "Phrase added!"

def update_phrase(phrase):
    data = json.load(open(words_to_track_file))
    for d in data["phrases"]:
        if d.get("phrase").lower() in phrase.lower():
            d["times_said"] += 1
    with open(words_to_track_file, "w") as f:
        f.write(json.dumps(data, indent=4))
        return "Updated phrase!"

def remove_phrase(phrase):
    data = json.load(open(words_to_track_file))
    with open(words_to_track_file, "w") as f:
        data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
        f.write(json.dumps(data, indent=4))
        return "Removed phrase!"


async def pin_archive():
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
        return "No more pins"
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
    await general_chat.send(f"Archived the pins! Check them out in #{archive_channel}!")


TOKEN = "NTIxNTUwNzIyMzU0MTE4NjY2.XqzV7Q.gvob9l9tcZe2_W_vH_54Y-shW1A"
client = discord.Client()

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
    mapping = [("buh!help ", ""), ("buh!add_phrase ", ""), ("buh!ap ", ""), ("buh!phrases_counts ", ""), ("buh!pc ", ""), ("buh!remove_phrase ", ""), ("buh!rp ", ""), ("buh!archive_pins ", ""), ("buh!arcp ", ""), ("buh!house_points ", ""), ("buh!hp", "")]
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
    elif any(com in message.content for com in ["buh!add_phrase", "buh!ap"]):
        for k, v in mapping:
            message.content = message.content.replace(k, v)
        await message.channel.send(add_phrase(message.content))
        return
    elif any(com in message.content for com in ["buh!remove_phrase", "buh!rp"]):
        for k, v in mapping:
            message.content = message.content.replace(k, v)
        await message.channel.send(remove_phrase(message.content))
    elif any(com == message.content for com in ["buh!phrases_counts", "buh!pc"]):
        data = json.load(open(words_to_track_file))
        string_to_print = ""
        for phrase in data["phrases"]:
            string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
        await message.channel.send(string_to_print)
        return
    elif any(com == message.content for com in ["buh!archive_pins", "buh!arcp"]):
        await pin_archive()
        return
    elif any(com == message.content for com in ["buh!house_points", "buh!hp"]):
        data = json.load(open(words_to_track_file))
        house_emb = discord.Embed(title="House points", colour=0x00adff)
        for house in data["houses"]:
            house_emb.add_field(name=house["house_name"], value=house["house_points"], inline=False)
        await message.channel.send(embed=house_emb)
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
