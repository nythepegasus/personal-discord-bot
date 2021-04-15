import asyncio
import itertools
import json
import os
import random
import typing
import arrow
import discord
from pathlib import Path
import matplotlib.pyplot as plt
import sentry_sdk
from discord.ext import commands


class PointsCog(commands.Cog, name="points"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self._scoreboard: discord.Message = None
        self.houses = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]
        self.house_points = "db_files/houses.json"
        self.client.pts_db_file = Path('db_files/points.json')
        self.client.random_phrases = Path('db_files/random_texts.json')

    async def cog_check(self, ctx):
        if len([i.name for i in ctx.author.roles if i.name in self.houses]) != 1:
            await ctx.send("Make sure you have 1 Hogwarts role prior to running points commands!", delete_after=10)
            return False
        else:
            return True

    async def cog_before_invoke(self, ctx):
        ctx.hs = json.load(open(self.house_points))
        try:
            ctx.plyr_data = json.load(open(f"db_files/players/{ctx.author.id}.json"))
        except FileNotFoundError:
            ctx.plyr_data = {
                "name": ctx.author.name,
                "house": [i.name for i in ctx.author.roles if i.name in self.houses][0],
                "points_earned": [],
                "season_history": [],
                "timeouts": {
                    "begging": ""
                },
                "items": [],
                "phrases": [],
                "command_usages": [],
                "misc_info": {}
            }
            if ctx.author.id not in ctx.hs[ctx.plyr_data['house']]['members']:
                ctx.hs[ctx.plyr_data['house']]['members'].append(ctx.author.id)

    async def cog_after_invoke(self, ctx):
        json.dump(ctx.plyr_data, open(f"db_files/players/{ctx.author.id}.json", "w"), indent=4)
        if ctx.command.name == "house_points":
            return
        if ctx.channel.name == "bot-commands" or ctx.channel.name == "mafia":
            h = await ctx.channel.history(limit=10).flatten()
            if self._scoreboard is None:
                return
            elif self._scoreboard in h:
                await self._scoreboard.edit(embed=self.house_pts_emb())
            else:
                await self._scoreboard.delete()
                self._scoreboard = None

    def season_helper(self):
        for player_file in Path("db_files/players/").iterdir():
            player_data = json.load(player_file.open())
            for to in player_data['timeouts']:
                player_data['timeouts'][to] = ""
            player_data['season_history'].append(player_data['points_earned'])
            player_data['points_earned'] = []
        data = json.load(open(self.client.pts_db_file))
        data['cur_season'] += 1
        json.dump(data, open(self.client.pts_db_file, "w"))

    def house_pts_emb(self, house_data: dict = None):
        if house_data is None:
            house_data = json.load(open(self.house_points))
        for house in house_data:
            house_points = 0
            for member in house_data[house]['members']:
                house_points += sum(json.load(open(f'db_files/players/{member}.json'))['points_earned'])
            house_data[house]['points'] = house_points
        json.dump(house_data, open(self.house_points, "w"), indent=4)
        house_emb = discord.Embed(title="House Points", colour=0x00adff)
        for house in house_data.items():
            house_emb.add_field(name=house[0], value=str(house[1]['points']), inline=False)
        return house_emb

    @commands.command(aliases=['hp'])
    async def house_points(self, ctx):
        if self._scoreboard is not None:
            await self._scoreboard.delete()
        self._scoreboard = await ctx.send(embed=self.house_pts_emb(ctx.hs))

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(aliases=["cs"])
    async def cast_spell(self, ctx):
        if random.random() >= 0.3:
            points_changed = random.randint(3, 10)
            if random.random() >= .5:
                points_changed = random.randint(10, 20)
        else:
            points_changed = random.randint(-25, -20)
            if random.random() <= .8:
                points_changed = random.randint(-10, -3)
        ctx.plyr_data["points_earned"].append(points_changed)
        emb = discord.Embed(title="Casting Spell", colour=0x00adff)
        chg = "gain" if points_changed > 0 else "lose"
        random_text = random.choice([i for i in json.load(open(self.client.random_phrases))["phrases"]
                                     if i["type"] == "spell" and i["points"] == chg])
        emb.description = random_text["text"].format(house=ctx.plyr_data['house'], points=abs(points_changed))
        if not random_text["author"] == "":
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, house_name):
        if house_name.capitalize() not in self.houses:
            await ctx.send("Couldn't find house!", delete_after=7)
            return
        if house_name.capitalize() == ctx.plyr_data["house"]:
            await ctx.send("You can't steal from your own house, what're you, crazy??", delete_after=10)
            return
        steal_file = f"db_files/players/{random.choice(ctx.hs[house_name.capitalize()]['members'])}.json"
        steal_from = json.load(open(steal_file))
        if random.random() >= .60:
            points_changed = random.randint(30, 45)
            if random.random() >= .80:
                points_changed = random.randint(50, 60)
        else:
            points_changed = random.randint(-25, -15)
            if random.random() <= .40:
                points_changed = random.randint(-45, -25)
        ctx.plyr_data['points_earned'].append(points_changed)
        steal_from['points_earned'].append(-points_changed)
        json.dump(steal_from, open(steal_file, "w"), indent=4)
        emb = discord.Embed(title="Stealing", colour=0x00adff)
        chg = "gain" if points_changed > 0 else "lose"
        random_text = random.choice([i for i in json.load(open(self.client.random_phrases))["phrases"]
                                     if i["type"] == "steal" and i["points"] == chg])
        emb.description = random_text["text"].format(house=steal_from['house'], points=abs(points_changed))
        if len(random_text["author"]) != 0:
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.command()
    async def beg(self, ctx):
        try:
            cur_timeout = arrow.get(ctx.plyr_data['timeouts']['begging'])
        except arrow.ParserError:
            cur_timeout = arrow.now()
        if arrow.now() > cur_timeout:
            ctx.plyr_data['timeouts']['begging'] = str(arrow.now().shift(days=1))
        else:
            await ctx.send(
                f"It seems you've begged a few too many times! Wait another "
                f"{cur_timeout.humanize(only_distance=True, granularity=['hour', 'minute'])}",
                delete_after=10)
            return
        if random.random() >= .35:
            points_awarded = random.randint(40, 70)
            chg = "big"
        else:
            if random.random() <= .05:
                ctx.plyr_data['points_earned'].append(150)
                emb = discord.Embed(title="**HOLY FUCKING SHIT!**", colour=0x00adff,
                                    description="Your luck just fuckin' turned around, bucko."
                                                " You just gained {} points for {}.".format(
                                        150, ctx.plyr_data['house']))
                emb.set_footer(text="From Dumbledore's Grace")
                return await ctx.send(embed=emb, delete_after=60)
            else:
                points_awarded = random.randint(25, 35)
                chg = "gain"
        random_text = random.choice([i for i in json.load(open(self.client.random_phrases))["phrases"]
                                     if i["type"] == "beg" and i["points"] == chg])
        ctx.plyr_data['points_earned'].append(points_awarded)
        emb = discord.Embed(
            title="Begging",
            colour=0x00adff,
            description=random_text["text"].format(house=ctx.plyr_data['house'], points=points_awarded)
        )
        if not random_text["author"] == "":
            emb.set_footer(text=f"Phrase provided from: {random_text['author']}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(aliases=['ps'])
    async def player_stats(self, ctx, player: typing.Optional[discord.User]):
        if player is not None:
            data = json.load(open(f"db_files/players/{player.id}.json"))
        else:
            data = ctx.plyr_data
        cur_player_diffs = list(itertools.accumulate(data['points_earned']))
        plt.clf()
        plt.plot([float(i) for i in range(0, len(cur_player_diffs) + 1)],
                 [0] + [float(i) for i in list(cur_player_diffs)])
        plt.xticks([float(i) for i in range(0, len(cur_player_diffs) + 1)])
        plt.yticks([float(i) for i in range(0, (max(cur_player_diffs) // 10 * 10) + 10, 10)])
        plt.grid(True)
        plt.savefig("{}.png".format(data['name']))
        emb = discord.Embed(
            title="{} Stats".format(data['name']),
            description="X-Axis is the amount of bot commands\nY-Axis is the amount of points."
        )
        await ctx.send(embed=emb)
        await ctx.send(file=discord.File("{}.png".format(data['name'])))
        os.remove("{}.png".format(data['name']))

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if channel.name != "general":
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.message_pin, limit=1):
            t = arrow.now().naive - entry.created_at
            if t.seconds == 0 or t.days < 0:
                giver = json.load(open(f"db_files/players/{entry.user.id}.json"))
                given = json.load(open(f"db_files/players/{entry.target.id}.json"))
                if giver['house'] != given['house']:
                    await channel.send(f"50 points to {given['house']}!")
                    await channel.send(f"(And 20 for {giver['house']} for finding such a spicy maymay ;))",
                                       delete_after=10)
                    given['points_earned'].append(50)
                else:
                    await channel.send(f"20 points for {given['house']}!")
                    await channel.send(f"Circlejerking has officially been nerfed.", delete_after=5)
                giver['points_earned'].append(20)
                json.dump(giver, open(f"db_files/players/{entry.user.id}.json", "w"), indent=4)
        p = await channel.pins()
        if len(p) == 50:
            self.season_helper()
            await ctx.invoke([i for i in self.client.commands if i.name == "archive_pins"][0])

    async def cog_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            await ctx.send(
                f"{ctx.message.author.mention} You're a little tired from your last fiasco. "
                f"Wait {round(error.retry_after, 2)} seconds to try again.", delete_after=10)
        else:
            await ctx.send("Something went wrong when sending the random text (Blame Tony, always blame Tony). Your "
                           "points should be there, but if not, they were eaten by the old Gods, and there's no "
                           "saving them. Better luck next time.")
            sentry_sdk.capture_exception(error)
            raise error


def setup(client):
    client.add_cog(PointsCog(client))
