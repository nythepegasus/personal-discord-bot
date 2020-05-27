import sys, traceback, discord
from discord.ext import commands


"""
Start of the variables and such for the backend.
"""


tonys_a_cunt = [
        "\u0628",
        "\u064d",
        "\u0631",
        "nigga",
        "nigger",
]

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
<<<<<<< HEAD
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
        if house["house_name"].lower() in ctx.message.content.lower():
            stolen_from = house
        else:
            await ctx.send("Why're you trying to steal from yourself? You're lucky your prefect ain't rapin' your ass for that.")
            return
    if random.randint(1, 10) >= 7:
        if random.randint(1, 10) >= 8:
            amount_stolen = random.randint(35, 45)
        else:
            amount_stolen = random.randint(25, 35)
        stolen_from["house_points"] -= amount_stolen
        stealer["house_points"] += amount_stolen
        await ctx.send(f'Your prefect found members of {stolen_from["house_name"]} fucking in the halls late at night.\nYour house stole {amount_stolen} points from their house!')
        json.dump(data, open(db_file, "w"))
        return
    else:
        amount_lost = random.randint(15, 20)
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
    if ctx.message.author.id in [i["person"] for i in data["timeouts"]]:
        for i in data["timeouts"]:
            if ctx.message.author.id == i["person"]:
                cur_timeout = time.gmtime(time.time() - i["timeout"])
                if cur_timeout.tm_hour < 24 and cur_timeout.tm_yday == 1 and cur_timeout.tm_year <= 1970:
                    await ctx.send(f'Dumbledore\'s cock has had enough of your mouth. Please wait {time.gmtime(i["timeout"] - time.time()).tm_hour} hours and {time.gmtime(i["timeout"] - time.time()).tm_min} minutes.')
                    return
                else:
                    i["timeout"] = time.time()
                    json.dump(data, open(db_file, "w"))
    else:
        person_timeout = {
            "person": ctx.message.author.id,
            "timeout": time.time()
        }
        data["timeouts"].append(person_timeout)
        json.dump(data, open(db_file, "w"))
    await ctx.send("You hear a zip sound come from under Dumbledore's robes..")
    for house in data["houses"]:
        if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
            da_house = house
        else:
            pass
    if random.randint(1, 10) >= 5:
        points_awarded = random.randint(40, 70)
        await ctx.send(f"Dumbledore seems very pleased with how you sucked his cock.\n{da_house['house_name']} earns {points_awarded} points for your awesome head skills!")
    else:
        points_awarded = random.randint(25, 35)
        await ctx.send(f"Dumbledore is somewhat okay with how you gave head. Just uh, use less teeth next time, got it?\n{points_awarded} points to {da_house['house_name']}.")
    da_house["house_points"] += points_awarded
    json.dump(data, open(db_file, "w"), indent=4)
=======
        client.load_extension(extension)
        print(f"Loaded {extension}.")
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()
>>>>>>> 97ca4078d09932122ed0301138a9e004b3b851c0


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
