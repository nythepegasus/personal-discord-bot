import os, json, datetime, time, psutil, discord, speedtest, subprocess, random
from discord.ext import commands


"""
Start of the variables and such for the backend.
"""


db_file = "phrases.json"


if not os.path.isfile(db_file):
    with open(db_file, "w") as f:
        f.write('{\n"phrases": [],\n"houses": [\n{\n"house_name": "Gryffindor",\n"house_points": 0\n},\n{\n"house_name": "Slytherin",\n"house_points": 0\n},\n{\n"house_name": "Ravenclaw",\n"house_points": 0\n},\n{\n"house_name": "Hufflepuff",\n"house_points": 0\n}\n],\n"last_pin_count": 0,\n"timeouts": []}')


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
    help_emb.add_field(name="buh!cast_spell | buh!cs", value="Gamble your house's points away, and see where fate takes you.", inline=False)
    help_emb.add_field(name="buh!stats", value="Check the discord bot's current server stats", inline=False)
    help_emb.add_field(name="buh!netstats", value="Check the discord bot's current net stats", inline=False)
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
            ctx.send("Phrase already exists!")
            return
        elif len(phrase) <= 2:
            ctx.send("Phrase too short!")
            return
        elif len(phrase) >= 35:
            ctx.send("Phrase too long!")
            return
        elif any(bad in phrase for bad in tonys_a_cunt):
            await ctx.send("You're a cunt!")
            return
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
    uptime = subprocess.run("uptime", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    days = int(uptime.stdout.split()[2])
    hours = str(int(uptime.stdout.split()[4].strip(b",").split(b":")[0])).zfill(2)
    minutes = str(int(uptime.stdout.split()[4].strip(b",").split(b":")[1])).zfill(2)
    stat_emb = discord.Embed(title="Discord Bot's Server Stats", colour=0x00adff)
    stat_emb.add_field(name="Current Uptime", value=f"{days}:{hours}:{minutes}")
    stat_emb.add_field(name="RAM Percentage", value=psutil.virtual_memory()[2])
    stat_emb.add_field(name="CPU Percentage", value=psutil.cpu_percent())
    stat_emb.set_footer(text="Proudly fixed with nano.")
    await ctx.send(embed=stat_emb)


@commands.cooldown(1, 120, commands.BucketType.user)
@client.command()
async def netstats(ctx):
    async with ctx.typing():
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download(threads=4)
        s.upload(threads=4)
        url = s.results.share()
        net_emb = discord.Embed(title="Discord Bot's Network Speeds", colour=0x00adff)
        net_emb.set_image(url=url)
        await ctx.send(embed=net_emb)


@netstats.error
async def netstats_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Wait {round(error.retry_after, 2)} more seconds.")
    else:
        raise error


@commands.cooldown(1, 180, commands.BucketType.user)
@client.command(aliases=["cs"])
async def cast_spell(ctx):
    data = json.load(open(db_file))
    if random.randint(1, 10) >= 6:
        if random.randint(1, 10) >= 8:
            points_awarded = random.randint(10, 20)
        else:
            points_awarded = random.randint(3, 10)
    else:
        if random.randint(1, 10) <= 8:
            points_reducted = random.randint(3, 10)
        else:
            points_reducted = random.randint(20, 25)
    for house in data["houses"]:
        if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
            da_house = house["house_name"]
            try:
                house["house_points"] += points_awarded
                with open(db_file, "w") as f:
                    f.write(json.dumps(data, indent=4))
                random_phrases_points_awarded = [
                    f"You handled your rod quite well!\n{points_awarded} points awarded to {da_house}!",
                    f"You sucked Umbridge's toes in whatever fucking class that bitch teaches.\n{da_house} gets {points_awarded} points, you fucking simp.",
                    f"You found a chocolate frog.\n{points_awarded} points awarded to {da_house}!",
                    f"You scored a banger goal in a Quidditch match and made the losing team cry like a bitch from your thick cock.\n{points_awarded} points to {da_house}!",
                    f"Moaning Myrtle saw your bomb ass cock.\n{points_awarded} points to {da_house} for pimpin' the ghost bitch.",
                    f"Your love potion turned out too well, now Snape's riding your cock.\n{points_awarded} points to {da_house}!",
                    f"You found Hagrid's secret stash of Hermione's nudes. (Don't tell anyone)\n{da_house} earns {points_awarded}! (As long as you keep quiet, you lil fuck)",
                    f"You smacked your prefect's ass for doing a good job. He gives you a thumbs up, smacks your ass, and winks at you.\n{points_awarded} points for {da_house}. (Someone's getting lucky tonight ;))",
                    f"You called Ron a ginger virgin, and everyone laughed (r/thathappened). Fuck you, Ron.\n{points_awarded} points for {da_house}.",
                    f"You got the mandrake to shut the fuck up (thank fuck).\n{points_awarded} points for {da_house}, you hero.",
                    f"Nearly Headless Nick nearly gave you head.\n{da_house} gets {points_awarded} points, since you're a sick fuck who likes the quick fuck",
                ]
                await ctx.send(random.choice(random_phrases_points_awarded))
            except NameError:
                try:
                    house["house_points"] -= points_reducted
                    with open(db_file, "w") as f:
                        f.write(json.dumps(data, indent=4))
                    random_phrases_points_reducted = [
                        f"You angered Snape in potions class.\n{points_reducted} points taken from {da_house}.",
                        f"You pronounced a spell wrong, it's pronounced levi*o*sa.\n{points_reducted} points taken from {da_house}.",
                        f"You fell up the stairs, you fucking idiot.\n{points_reducted} points taken from {da_house}.",
                        f"You fell down 10 flights on the Grand Staircase and broke 24 bones and are now hospitalized for a week.\n\nOh, and {da_house} loses {points_reducted} points. Nice goin'",
                        f"Voldemort smote the school because you made fun of his not nose. Way to go, dickhead.\n{da_house} loses {points_reducted} points. (You should feel bad, sick fuck).",
                        f"You got wasted on nonalcoholic butterbeer like an underaged cuck, and started a petty brawl.\n{points_reducted} points from {da_house}.",
                        f"You creeped out Hagrid with your weird ass fanfiction about his giant furcock.\n{da_house} loses {points_reducted} points.",
                        f"You let the Cornish Pixies escape from their cage and they wreaked havoc around the school. Good job, dumbass.\n{da_house} loses {points_reducted} points because of your dumbassery.",
                    ]
                    await ctx.send(random.choice(random_phrases_points_reducted))
                except NameError:
                    await ctx.send("Something went terribly, terribly wrong. Please tell <@195864152856723456> to fix his jank shit.")
        else:
            pass


@cast_spell.error
async def cast_spell_erorr(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
    else:
        raise error


@commands.cooldown(1, 600, commands.BucketType.user)
@client.command()
async def steal(ctx):
    data = json.load(open(db_file))
    houses_steal_from = data["houses"].copy()
    for house in houses_steal_from:
        if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
            stealer = houses_steal_from.pop(houses_steal_from.index(house))
    for house in houses_steal_from:
        if house["house_name"] in ctx.message.content:
            stolen_from = house
    if random.randint(1, 10) >= 7:
        if random.randint(1, 10) >= 8:
            amount_stolen = random.randint(20, 30)
        else:
            amount_stolen = random.randint(5, 15)
        stolen_from["house_points"] -= amount_stolen
        stealer["house_points"] += amount_stolen
        await ctx.send(f'Your prefect found members of {stolen_from["house_name"]} fucking in the halls late at night.\nYour house stole {amount_stolen} points from their house!')
        json.dump(data, open(db_file, "w"))
        return
    else:
        amount_lost = random.randint(6, 16)
        if random.randint(1,10) <= 4:
            amount_lost = random.randint(25, 35)
        stolen_from["house_points"] += amount_lost
        stealer["house_points"] -= amount_lost
        await ctx.send(f'{stolen_from["house_name"]}\'s prefect found you bumbling about trying to spy on them. Your house gave them {amount_lost} points.')
        json.dump(data, open(db_file, "w"))
        return


@steal.error
async def steal_erorr(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
    else:
        raise error


@client.command()
async def beg(ctx):
    data = json.load(open(db_file))
    for i in data["timeouts"]:
        if ctx.message.author.discriminator == i["person"]:
            if time.strftime("%H", time.gmtime((i["timeout"] - time.time()))) < "24":
                await ctx.send(f'Dumbledore\'s cock has had enough of your mouth. Please wait {int(time.strftime("%H", time.gmtime((i["timeout"] - time.time()))))} hours.')
                return
    person_timeout = {
        "person": ctx.message.author.discriminator,
        "timeout": time.time()
    }
    data["timeouts"].append(person_timeout)
    json.dump(data, open(db_file, "w"))
    await ctx.send("You hear a zip sound come from under Dumbledore's robes..")
    if random.randint(1, 10) >= 5:
        points_awarded = random.randint(40, 70)
        big_award = True
    else:
        points_awarded = random.randint(25, 35)
        big_award = False
    for house in data["houses"]:
        if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
            da_house = house["house_name"]
            house["house_points"] += points_awarded
            with open(db_file, "w") as f:
                f.write(json.dumps(data, indent=4))
        else:
            pass
    if big_award:
        await ctx.send(f"Dumbledore seems very pleased with how you sucked his cock.\n{da_house} earns {points_awarded} points for your awesome head skills!")
    else:
        await ctx.send(f"Dumbledore is somewhat okay with how you gave head. Just uh, use less teeth next time, got it?\n{points_awarded} points to {da_house}.")


"""
Starting the events, such as messages and pins.
"""


@client.event
async def on_ready():
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
        return
    update_phrase(message.content)
    await client.process_commands(message)


@client.event
async def on_message_delete(message):
    user = client.get_user(195864152856723456)
    emb = discord.Embed(
        description = message.content,
        timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
    )
    emb.set_author(
        name=message.author,
        icon_url=message.author.avatar_url,
        url="https://discordapp.com/channels/{0}/{1}/{2}".format(
            message.guild.id, message.channel.id, message.id)
    )
    if message.attachments:
        if len(message.attachments) > 1:
            img_url = message.attachments[0].url
            emb.set_image(url=img_url)
            emb.set_footer(text=f"Part 1 | Archived from #{message.channel}")
            await user.send(embed=emb)
            attach_counter = 1
            try:
                for attachment in message.attachments:
                    next_emb = discord.Embed(
                        timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
                    )
                    next_emb.set_author(
                    name=message.author,
                    icon_url=message.author.avatar_url,
                    url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                        message.guild.id, message.channel.id, message.id)
                    )
                    img_url = message.attachments[attach_counter].url
                    next_emb.set_image(url=img_url)
                    next_emb.set_footer(text=f"Part {attach_counter+1} | Deleted from #{message.channel}")
                    attach_counter += 1
                    await user.send(embed=next_emb)
            except IndexError:
                pass
        elif len(message.attachments) == 1:
            img_url = message.attachments[0].url
            emb.set_image(url=img_url)
            emb.set_footer(text=f"Deleted from #{message.channel}")
            await user.send(embed=emb)
    else:
        await user.send(embed=emb)

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
                    house["house_points"] += 50
                else:
                    pass
            with open(db_file, "w") as f:
                f.write(json.dumps(data, indent=4))
            await channel.send(f"50 points to {da_house}!")
        except IndexError:
            pass


client.run(TOKEN)
