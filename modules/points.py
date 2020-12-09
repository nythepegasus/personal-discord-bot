import json
import random
import datetime
import discord
import asyncio
from discord.ext import commands


class PointsCog(commands.Cog, name="Points Commands"):
    def __init__(self, client: "Bot client"):
        self.client = client
        self.db_file = 'db_files/points.json'
        self.random_phrases = 'db_files/random_texts.json'

    def season_helper(self):
        data = json.load(open(self.db_file))
        if data["last_pin_count"] == 50:
            data["cur_season"] += 1
            data["timeouts"] = []
            for house in data["houses"]:
                house["history"].append(house["house_points"])
                house["house_points"] = 0
            json.dump(data, open("db_files/points.json", "w"), indent=4)

    @commands.command(aliases=["hp"])
    async def house_points(self, ctx):
        await ctx.message.delete()
        data = json.load(open(self.db_file))
        house_emb = discord.Embed(title="House points", colour=0x00adff)
        for house in data["houses"]:
            house_emb.add_field(name=house["house_name"], value=house["house_points"], inline=False)
        await ctx.send(embed=house_emb)

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(aliases=["cs"])
    async def cast_spell(self, ctx):
        await ctx.message.delete()
        data = json.load(open(self.db_file))
        if random.randint(1, 10) >= 5:
            if random.randint(1, 10) >= 5:
                points_changed = random.randint(10, 20)
            else:
                points_changed = random.randint(3, 10)
        else:
            if random.randint(1, 10) <= 8:
                points_changed = random.randint(-10, -3)
            else:
                points_changed = random.randint(-25, -20)
        for house in data["houses"]:
            if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
                da_house = house["house_name"]
                house["house_points"] += points_changed
                json.dump(data, open(self.db_file, "w"), indent=4)
                emb = discord.Embed(title="Casting Spell", colour=0x00adff)
                if points_changed > 0:
                    random_text = random.choice(json.load(open(self.random_phrases))["spell_texts"]["gain_texts"])
                    emb.description = random_text["gain_text"].format(house=da_house, points=abs(points_changed))
                else:
                    random_text = random.choice(json.load(open(self.random_phrases))["spell_texts"]["lose_texts"])
                    emb.description = random_text["lose_text"].format(house=da_house, points=abs(points_changed))
                if len(random_text["author"]) != 0:
                    emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
                await ctx.send(embed=emb)
                return
        await ctx.send("You should have a Hogwarts role before you run this command!")

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, house_name):
        await ctx.message.delete()
        data = json.load(open(self.db_file))
        houses_steal_from = data["houses"].copy()
        for house in houses_steal_from:
            if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
                stealing_house_name = house
        for house in houses_steal_from:
            if house["house_name"].lower() == house_name.lower():
                stolen_from = house
                break
        if stolen_from == stealing_house_name:
            await ctx.send("Why're you trying to steal from yourself? You're lucky your prefect ain't rapin' your ass for that.")
            return
        if random.randint(1, 10) >= 7:
            amount_changed = random.randint(25, 35)
            if random.randint(1, 10) >= 8:
                amount_changed = random.randint(35, 45)
        else:
            amount_changed = random.randint(-20, -15)
            if random.randint(1, 10) <= 4:
                amount_changed = random.randint(-35, -25)
        stolen_from["house_points"] -= amount_changed
        stealing_house_name["house_points"] += amount_changed
        json.dump(data, open(self.db_file, "w"), indent=4)
        emb = discord.Embed(title="Stealing", colour=0x00adff)
        if amount_changed > 0:
            random_text = random.choice(json.load(open(self.random_phrases))["steal_texts"]["gain_texts"])
            emb.description = random_text["gain_text"].format(house=stolen_from["house_name"], points=amount_changed)
        else:
            random_text = random.choice(json.load(open(self.random_phrases))["steal_texts"]["lose_texts"])
            emb.description = random_text["lose_text"].format(house=stolen_from["house_name"], points=abs(amount_changed))
        if len(random_text["author"]) != 0:
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb)
        return

    @commands.command()
    async def beg(self, ctx):
        await ctx.message.delete()
        data = json.load(open(self.db_file))
        if ctx.message.author.id in [i["person"] for i in data["timeouts"]]:
            for i in data["timeouts"]:
                if ctx.message.author.id == i["person"]:
                    cur_time = datetime.datetime.now()
                    cur_timeout = datetime.datetime.strptime(i["timeout"], '%Y-%m-%dT%H:%M:%S.%f')
                    if cur_time < cur_timeout:
                        await ctx.send(
                            f"It seems you've begged a few too many times. Give it {(cur_timeout - cur_time).seconds // 3600} hours and {((cur_timeout - cur_time).seconds // 60) % 60} minutes.")
                        return
                    else:
                        i["timeout"] = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
                        json.dump(data, open(self.db_file, "w"), indent=4)
        else:
            person_timeout = {
                "person": ctx.message.author.id,
                "timeout": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }
            data["timeouts"].append(person_timeout)
            json.dump(data, open(self.db_file, "w"), indent=4)
        for house in data["houses"]:
            if house["house_name"].lower() in [y.name.lower() for y in ctx.author.roles]:
                da_house = house
            else:
                pass
        if random.randint(1, 10) >= 5:
            points_awarded = random.randint(40, 70)
            random_text = random.choice(json.load(open(self.random_phrases))["beg_texts"]["big_gain_texts"])
        else:
            if random.randint(1, 10) <= 2:
                points_awarded = 150
                emb = discord.Embed(title="**HOLY FUCKING SHIT!**", colour=0x00adff, description="Your luck just fuckin' turned around, bucko. You just gained {} points for {}.".format(points_awarded, da_house["house_name"]))
                emb.set_footer(text="From Dumbledore's Grace")
                await ctx.send(embed=emb)
            else:
                points_awarded = random.randint(25, 35)
                random_text = random.choice(json.load(open(self.random_phrases))["beg_texts"]["gain_texts"])
        da_house["house_points"] += points_awarded
        json.dump(data, open(self.db_file, "w"), indent=4)
        emb = discord.Embed(
            title="Begging",
            colour=0x00adff,
            description=random_text["gain_text"].format(house=da_house["house_name"], points=points_awarded)
        )
        if not random_text["author"] == "":
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb)

    @commands.command()
    async def starvetodeath(self, ctx):
        data = json.load(open(self.db_file))
        await ctx.message.delete()
        if data["commie_times"] != 5:
            await ctx.send(data["commie_strings"][data["commie_times"]])
            data["commie_times"] += 1
            json.dump(data, open(self.db_file, "w"), indent=4)
            return
        elif data["commie_ran"]:
            msg = await ctx.send("What's done is done, and cannot be done again.\n\n*For now..*")
            await msg.delete(delay=5)
            return
        elif data["last_pin_count"] <= 40:
            msg = await ctx.send("It's much too early for this.. Why not enjoy life for a while?\n*At least, while you still can.*")
            await msg.delete(delay=5)
            return
        await ctx.send(f"Oooo, you've done the thing, {ctx.author.mention}. What you have done cannot be reversed. I hope you realize that, and I hope you're okay with the consequences.")
        await ctx.send("Operation done in..")
        nums = list(range(0, 11))
        nums.reverse()
        for i in nums:
            num = await ctx.send(f"{i}..")
            await asyncio.sleep(5)
            await num.delete()
        communism = 0
        for i in data["houses"]:
            communism += i["house_points"]
        communism /= 4
        for i in data["houses"]:
            i["house_points"] = int(communism)+1
        data["commie_ran"] = True
        json.dump(data, open(self.db_file, "w"), indent=4)
        await ctx.send("What's done is done.\nMomento mori.")


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user:
            return
        channel = reaction.message.channel
        if channel.name == "general" and reaction.emoji == u"\U0001F4CC":
            message = reaction.message
            await message.pin()
            data = json.load(open(self.db_file, "w"))
            myPins = await channel.pins()
            data["last_pin_count"] = len(myPins)
            if data["last_pin_count"] > len(myPins):
                json.dump(data, open(self.db_file, "w"), indent=4)
                return
            else:
                try:
                    for house in data["houses"]:
                        if house["house_name"].lower() in [y.name.lower() for y in message.author.roles]:
                            da_house = house["house_name"]
                            house["house_points"] += 50
                        else:
                            pass
                except IndexError:
                    await channel.send("<@195864152856723456>\nPin Error: Awarded house cannot be found!\nManually add points, and find your fuckup.")
                    return
                try:
                    for house in data["houses"]:
                        if house["house_name"].lower() in [y.name.lower() for y in user.roles]:
                            de_house = house["house_name"]
                            house["house_points"] += 30
                        else:
                            pass
                    with open(self.db_file, "w") as f:
                        f.write(json.dumps(data, indent=4))
                except IndexError:
                    await channel.send("<@195864152856723456>\nPin Error: Awarder house cannot be found!\nManually add points, and find your fuckup.")
                    return
                await channel.send(f"30 points to {de_house}, and 50 points to {da_house}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = self.client.guilds[0]
        for channel in guild.channels:
            if channel.name == "general":
                general_chat = channel
                self.season_helper()

    async def cog_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
        elif isinstance(error, KeyError):
            await ctx.send("Something went wrong when sending the random text (Blame Tony, always blame Tony). Your "
                           "points should be there, but if not, they were eaten by the old Gods, and there's no "
                           "saving them. Better luck next time.")
        else:
            raise error
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return


def setup(client):
    client.add_cog(PointsCog(client))
