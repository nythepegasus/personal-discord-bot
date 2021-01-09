import json
import random
import datetime
import discord
import asyncio
import sentry_sdk
from discord.ext import commands

sentry_sdk.init(
    json.load(open("conf_files/conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)

class PointsCog(commands.Cog, name="Points Commands"):
    def __init__(self, client: "Bot client"):
        self.client = client
        self.houses = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]
        self.db_file = 'db_files/points.json'
        self.random_phrases = 'db_files/random_texts.json'

    class Player(object):
        def __init__(self, id: int, data: dict = None):
            """
            :param id: The player's id
            :param data: Data is a dictionary of the player data if they've been created
                :var name: The player's name for easier identification
                :var house: This will make it easier for me to keep track of houses
                :var season_history: The season history of the current player
                :var timeout: The player's current timeout
                :var points_earned: The amount of points that a player has earned this season
                :var items: A list of Item objects, or the player's inventory
            """
            self.id = id
            if data is not None:
                self.name = data["name"]  # -> str
                self.house = data["house"]  # -> str
                self.season_history = data["season_history"]  # -> list[list[int]]
                self.timeout = data["timeout"]  # -> str
                self.points_earned = list(data["points_earned"]) # -> list[int]
                self.items = data["items"]  # -> list<Item>
            else:
                return

        @property
        def player_json(self):
            return {str(self.id): {"name": self.name, "house": self.house, "season_history": self.season_history,
                                      "timeout": self.timeout, "points_earned": self.points_earned,
                                      "items": self.items}}

        def __str__(self):
            return json.dumps(
                {self.name: {"timeout": self.timeout, "points_earned": sum(self.points_earned), "items": self.items}},
                indent=4)

        def __repr__(self):
            return f"Player({self.name}, {self.timeout}, {sum(self.points_earned)}, {self.items})"

        class Item(object):
            def __init__(self, name: str, value: int, quantity: int):
                """
                :param name: The item's name
                :param value: The item's value
                :param quantity: Number of items
                """
                self.name = name
                self.value = value
                self.quantity = quantity
                self.item_json = {self.name: {"value": self.value, "quantity": self.quantity}}

            def __repr__(self):
                return f"Item({self.name}, {self.value}, {self.quantity})"

            def __str__(self):
                return json.dumps({self.name: {"value": self.value, "quantity": self.quantity}}, indent=4)

        def add_item(self, name: str, value: int, quantity: int):
            """
            Add an item to the player's inventory
            :param name: Name of the item
            :param value: Value of the item
            :param quantity: Quantity of the item
            :return:
            """
            self.items.append(self.Item(name, value, quantity).item_json)

    async def player_helper(self, user):
        data = json.load(open(self.db_file))
        try:
            cur_player = self.Player(user.id, data=data["members"][str(user.id)])
            return cur_player
        except KeyError:
            roles = set(set(self.houses)).intersection(set([i.name for i in user.roles]))
            if roles == set():
                await ctx.send("You should have a Hogwarts role before you run this command!")
                return 1
            elif len(roles) > 1:
                await ctx.send("You have too many roles!")
                return 1
            else:
                return self.Player(user.id, {"name": user.name, "house": list(roles)[0], "season_history": [], "timeout": "", "points_earned": [], "items": []})

    def season_helper(self):
        data = json.load(open(self.db_file))
        for k, v in data["members"].items():
            v["timeouts"] = ""
            v["season_history"].append(v["points_earned"])
            v["points_earned"] = []
        data["cur_season"] += 1
        json.dump(data, open(self.db_file, "w"), indent=4)

    @commands.command(aliases=["hp"])
    async def house_points(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        data = json.load(open(self.db_file))
        house_emb = discord.Embed(title="House points", colour=0x00adff)
        for house in self.houses:
            house_points = 0
            for member in list(data["members"].keys()):
                cur_player = self.Player(member, data["members"][member])
                if house == cur_player.house:
                    house_points += sum(cur_player.points_earned)
            house_emb.add_field(name=house, value=str(house_points), inline=False)
        await ctx.send(embed=house_emb)

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(aliases=["cs"])
    async def cast_spell(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        cur_player = await self.player_helper(ctx.message.author)
        if cur_player == 1:
            return
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
        cur_player.points_earned.append(points_changed)
        data["members"].update(cur_player.player_json)
        json.dump(data, open(self.db_file, "w"), indent=4)
        emb = discord.Embed(title="Casting Spell", colour=0x00adff)
        if points_changed > 0:
            random_text = random.choice(json.load(open(self.random_phrases))["spell_texts"]["gain_texts"])
        else:
            random_text = random.choice(json.load(open(self.random_phrases))["spell_texts"]["lose_texts"])
        emb.description = random_text["text"].format(house=cur_player.house, points=abs(points_changed))
        if not random_text["author"] == "":
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, house_name):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        if house_name.capitalize() not in self.houses:
            msg = await ctx.send("Couldn't find house!")
            await msg.delete(delay=7)
            return
        cur_player = await self.player_helper(ctx.message.author)
        data = json.load(open(self.db_file))
        if house_name.capitalize() == cur_player.house:
            await ctx.send("Why're you trying to steal from yourself? You're lucky your prefect ain't rapin' your ass for that.")
            return
        to_steal_from = random.choice(list({key:val for key, val in data["members"].items() if val["house"] == house_name.capitalize()}.items()))
        stole_player = self.Player(to_steal_from[0], data=to_steal_from[1])
        if random.randint(1, 10) >= 7:
            amount_changed = random.randint(25, 35)
            if random.randint(1, 10) >= 8:
                amount_changed = random.randint(35, 45)
        else:
            amount_changed = random.randint(-20, -15)
            if random.randint(1, 10) <= 4:
                amount_changed = random.randint(-35, -25)
        cur_player.points_earned.append(amount_changed)
        stole_player.points_earned.append(amount_changed)
        data["members"].update(cur_player.player_json)
        data["members"].update(stole_player.player_json)
        json.dump(data, open(self.db_file, "w"), indent=4)
        emb = discord.Embed(title="Stealing", colour=0x00adff)
        if amount_changed > 0:
            random_text = random.choice(json.load(open(self.random_phrases))["steal_texts"]["gain_texts"])
            emb.description = random_text["text"].format(house=stole_player.house, points=amount_changed)
        else:
            random_text = random.choice(json.load(open(self.random_phrases))["steal_texts"]["lose_texts"])
            emb.description = random_text["text"].format(house=stole_player.house, points=abs(amount_changed))
        if len(random_text["author"]) != 0:
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb)
        return

    @commands.command()
    async def beg(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        cur_player = await self.player_helper(ctx.message.author)
        if cur_player == 1:
            return
        data = json.load(open(self.db_file))
        cur_time = datetime.datetime.now()
        try:
            cur_timeout = datetime.datetime.strptime(cur_player.timeout, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            cur_timeout = datetime.datetime.min
        if cur_time > cur_timeout:
            cur_player.timeout = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        else:
            await ctx.send(f"It seems you've begged a few too many times. Give it {(cur_timeout - cur_time).seconds // 3600} hours and {((cur_timeout - cur_time).seconds // 60) % 60} minutes.")
            return
        if random.randint(1, 10) >= 5:
            points_awarded = random.randint(40, 70)
            random_text = random.choice(json.load(open(self.random_phrases))["beg_texts"]["big_gain_texts"])
        else:
            if random.randint(1, 10) <= 2:
                points_awarded = 150
                emb = discord.Embed(title="**HOLY FUCKING SHIT!**", colour=0x00adff, description="Your luck just fuckin' turned around, bucko. You just gained {} points for {}.".format(points_awarded, cur_player.house))
                emb.set_footer(text="From Dumbledore's Grace")
                await ctx.send(embed=emb)
            else:
                points_awarded = random.randint(25, 35)
                random_text = random.choice(json.load(open(self.random_phrases))["beg_texts"]["gain_texts"])
        cur_player.points_earned.append(points_awarded)
        data["members"].update(cur_player.player_json)
        json.dump(data, open(self.db_file, "w"), indent=4)
        emb = discord.Embed(
            title="Begging",
            colour=0x00adff,
            description=random_text["text"].format(house=cur_player.house, points=points_awarded)
        )
        if not random_text["author"] == "":
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb)

    @commands.command()
    async def starvetodeath(self, ctx):
        data = json.load(open(self.db_file))
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
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
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if channel.name != "general":
            return
        data = json.load(open(self.db_file))
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.message_pin, limit=1):
            t = datetime.datetime.utcnow() - entry.created_at
            if t.seconds == 0 or t.days < 0:
                giver = await self.player_helper(channel.guild.get_member(entry.user.id))
                given = await self.player_helper(channel.guild.get_member(entry.target.id))
                given.points_earned.append(50)
                await channel.send(f"50 points to {given.house}!")
                if giver.house != given.house:
                    temp = await channel.send(f"(And 20 for {giver.house} for finding such a spicy maymay ;))")
                    await temp.delete(delay=10)
                    giver.points_earned.append(20)
                    data["members"].update(giver.player_json)
                print(data["members"][str(given.id)])
                data["members"].update(given.player_json)
                json.dump(data, open(self.db_file, "w"), indent=4)
                p = await channel.pins()
                if len(p) == 50:
                    self.season_helper()
                    await channel.send("End of season!")
        return

    async def cog_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""
        sentry_sdk.capture_exception(error)
        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            msg = await ctx.send(
                f"{ctx.message.author.mention} You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
            await msg.delete(delay=7)
        # elif isinstance(error, KeyError):
        #     await ctx.send("Something went wrong when sending the random text (Blame Tony, always blame Tony). Your "
        #                    "points should be there, but if not, they were eaten by the old Gods, and there's no "
        #                    "saving them. Better luck next time.")
        else:
            raise error
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return


def setup(client):
    client.add_cog(PointsCog(client))
