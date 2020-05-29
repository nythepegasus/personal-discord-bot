import discord
import json
import random
import time
from discord.ext import commands


class PointsCog(commands.Cog, name="Points Commands"):
    def __init__(self, client):
        self.client = client
        self.db_file = 'points.json'

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
                    json.dump(data, open(self.db_file, "w"), indent=4)
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
                        json.dump(data, open(self.db_file, "w"), indent=4)
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
    async def cast_spell_erorr(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
        else:
            raise error

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, house_name):
        data = json.load(open(self.db_file))
        houses_steal_from = data["houses"].copy()
        print([y.name for y in ctx.author.roles])
        print(houses_steal_from)
        print(house_name.lower())
        for house in houses_steal_from:
            if house["house_name"] in [y.name for y in ctx.author.roles]:
                stealer = houses_steal_from.pop(houses_steal_from.index(house))
        for house in houses_steal_from:
            print("Running to find steal_from")
            print(house["house_name"].lower())
            print(house_name.lower())
            if house["house_name"].lower() == house_name.lower():
                print("I ran, weirdly")
                stolen_from = house
        if stealer == stolen_from:
            await ctx.send("Why're you trying to steal from yourself? You're lucky your prefect ain't rapin' your ass for that.")
            return
        else:
            await ctx.send("Something maybe went right?.")
            await ctx.send(f"Variables:")
            await ctx.send(f"Stealer: {stealer}")
            await ctx.send(f"Stolen from: {stolen_from}")
        if random.randint(1, 10) >= 7:
            if random.randint(1, 10) >= 8:
                amount_stolen = random.randint(35, 45)
            else:
                amount_stolen = random.randint(25, 35)
            stolen_from["house_points"] -= amount_stolen
            stealer["house_points"] += amount_stolen
            await ctx.send(f'Your prefect found members of {stolen_from["house_name"]} fucking in the halls late at night.\nYour house stole {amount_stolen} points from their house!')
            json.dump(data, open(self.db_file, "w"), indent=4)
            return
        else:
            amount_lost = random.randint(15, 20)
            if random.randint(1, 10) <= 4:
                amount_lost = random.randint(25, 35)
            stolen_from["house_points"] += amount_lost
            stealer["house_points"] -= amount_lost
            await ctx.send(f'{stolen_from["house_name"]}\'s prefect found you bumbling about trying to spy on them. Your house gave them {amount_lost} points.')
            json.dump(data, open(self.db_file, "w"), indent=4)
            return

    @steal.error
    async def steal_erorr(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're a little tired from your last fiasco. Wait {round(error.retry_after, 2)} seconds to try again.")
        else:
            raise error

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
        json.dump(data, open(self.db_file, "w"), indent=4)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if channel.name != "general":
            return
        data = json.load(open(self.db_file))
        myPins = await channel.pins()
        if data["last_pin_count"] > len(myPins):
            data["last_pin_count"] = len(myPins)
            with open(self.db_file, "w") as f:
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
                with open(self.db_file, "w") as f:
                    f.write(json.dumps(data, indent=4))
                await channel.send(f"50 points to {da_house}!")
            except IndexError:
                pass


def setup(client):
    client.add_cog(PointsCog(client))
