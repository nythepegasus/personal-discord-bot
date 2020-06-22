import discord
import json
import random
import time
from discord.ext import commands


class PointsCog(commands.Cog, name="Points Commands"):
    def __init__(self, client: "Bot client"):
        self.client = client
        self.db_file = 'db_files/points.json'
        self.random_phrases = 'db_files/random_texts.json'

    @commands.command(aliases=["hp"])
    async def house_points(self, ctx):
        data = json.load(open(self.db_file))
        house_emb = discord.Embed(title="House points", colour=0x00adff)
        for house in data["houses"]:
            house_emb.add_field(name=house["house_name"], value=house["house_points"], inline=False)
        await ctx.send(embed=house_emb)

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(aliases=["cs"])
    async def cast_spell(self, ctx):
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
        data = json.load(open(self.db_file))
        if ctx.message.author.id in [i["person"] for i in data["timeouts"]]:
            for i in data["timeouts"]:
                if ctx.message.author.id == i["person"]:
                    cur_timeout = time.gmtime(time.time() - i["timeout"])
                    if cur_timeout.tm_hour < 24 and cur_timeout.tm_yday == 1 and cur_timeout.tm_year <= 1970:
                        await ctx.send(f'Dumbledore\'s cock has had enough of your mouth. Please wait {time.gmtime(i["timeout"] - time.time()).tm_hour} hours and {time.gmtime(i["timeout"] - time.time()).tm_min} minutes.')
                        return
                    else:
                        i["timeout"] = time.time()
                        json.dump(data, open(self.db_file, "w"), indent=4)
        else:
            person_timeout = {
                "person": ctx.message.author.id,
                "timeout": time.time()
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
            emb = discord.Embed(
                title="Begging",
                colour=0x00adff,
                description = random_text["gain_text"].format(house=da_house["house_name"], points=points_awarded)
            )
            if len(random_text["author"]) != 0:
                emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
            await ctx.send(embed=emb)
        else:
            if random.randint(1, 10) <= 2:
                points_awarded = 150
                emb = discord.Embed(title="**HOLY FUCKING SHIT!**", colour=0x00adff, description="Your luck just fuckin' turned around, bucko. You just gained {} points for {}.".format(points_awarded, da_house["house_name"]))
                emb.set_footer(text="From Dumbledore's Grace")
                await ctx.send(embed=emb)
            else:
                points_awarded = random.randint(25, 35)
                random_text = random.choice(json.load(open(self.random_phrases))["beg_texts"]["gain_texts"])
                emb = discord.Embed(
                    title="Begging",
                    colour=0x00adff,
                    description = random_text["gain_text"].format(house=da_house["house_name"], points=points_awarded)
                )
                if len(random_text["author"]) != 0:
                    emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
                await ctx.send(embed=emb)
        da_house["house_points"] += points_awarded
        json.dump(data, open(self.db_file, "w"), indent=4)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if channel.name != "general":
            return
        data = json.load(open(self.db_file))
        myPins = await channel.pins()
        if data["last_pin_count"] > len(myPins):
            data["last_pin_count"] = len(myPins)
            json.dump(data, open(self.db_file, "w"), indent=4)
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
                with open(self.db_file, "w") as f:
                    f.write(json.dumps(data, indent=4))
                await channel.send(f"50 points to {da_house}!")
            except IndexError:
                pass

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
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(
                f"Season's over for now! All the commands are all disabled until the next season begins!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
        else:
            raise error
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return



def setup(client):
    client.add_cog(PointsCog(client))
