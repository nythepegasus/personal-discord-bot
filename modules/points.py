import itertools
import json
import os
import random
import sys
import typing
import arrow
import discord
import matplotlib.pyplot as plt
import sentry_sdk
from discord.ext import commands
from utils.schema import Player, Points, RandomText, Timeout


class PointsCog(commands.Cog, name="Points"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.description = "This module adds the economy of Hogwarts to the server."
        self._scoreboard: discord.Message = None
        self.houses = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]
        self.season = json.load(open("db_files/points.json"))['cur_season']

    async def cog_check(self, ctx):
        if len([i.name for i in ctx.author.roles if i.name in self.houses]) != 1:
            chsmsg = await ctx.send("Please choose a house!")
            msg = await self.client.wait_for("message", timeout=60, check=lambda msg: msg.author == ctx.author)
            await chsmsg.delete()
            await msg.delete()
            if msg.content.capitalize() in self.houses:
                role = [i for i in ctx.guild.roles if i.name == msg.content.capitalize()][0]
                await ctx.author.add_roles(role)
                return True
            else:
                await ctx.send("House not found!", delete_after=7)
                return False
        else:
            return True

    async def cog_before_invoke(self, ctx: discord.ext.commands.Context):
        ctx.player = Player.objects(dis_id=str(ctx.author.id)).first()
        if ctx.player is None:
            ctx.player = Player(dis_id=str(ctx.author.id),
                                name=ctx.author.name,
                                house=[i.name for i in ctx.author.roles if i.name in self.houses][0],
                                items=[]).save()

    async def cog_after_invoke(self, ctx):
        if ctx.command.name == "house_points":
            return
        if ctx.channel.name == "bot-commands" or ctx.channel.name == "mafia":
            if self._scoreboard is None:
                return
            elif self._scoreboard in await ctx.channel.history(limit=10).flatten():
                house_emb = discord.Embed(title="House Points", colour=int(ctx.player.emb_conf['color'], 16))
                for house in self.houses:
                    house_emb.add_field(name=house, value=Points.objects(house=house, season=self.season).sum('points'),
                                        inline=False)
                await self._scoreboard.edit(embed=house_emb)
            else:
                await self._scoreboard.delete()
                self._scoreboard = None

    def season_helper(self):
        for i in Timeout.objects:
            i.update(until=arrow.now().naive)
        data = json.load(open(self.client.pts_db_file))
        data['cur_season'] += 1
        json.dump(data, open(self.client.pts_db_file, "w"))

    @commands.command(aliases=['hp'])
    async def house_points(self, ctx):
        if self._scoreboard is not None:
            await self._scoreboard.delete()
        house_emb = discord.Embed(title="House Points", colour=int(ctx.player.emb_conf['color'], 16))
        for house in self.houses:
            house_emb.add_field(name=house, value=Points.objects(house=house, season=self.season).sum('points'), inline=False)
        self._scoreboard = await ctx.send(embed=house_emb)

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
        Points(player=ctx.player, house=ctx.player.house, type="spell", points=points_changed, season=self.season).save()
        emb = discord.Embed(title="Casting Spell", colour=int(ctx.player.emb_conf['color'], 16))
        chg = "gain" if points_changed > 0 else "lose"
        random_text = random.choice(RandomText.objects(type="spell", points=chg))
        emb.description = random_text.text.format(house=ctx.player.house, points=abs(points_changed))
        if not random_text.author == "":
            emb.set_footer(text=f"Phrase provided from: {random_text.author}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, house_name):
        if house_name.capitalize() not in self.houses:
            await ctx.send("Couldn't find house!", delete_after=7)
            return
        if house_name.capitalize() == ctx.player.house:
            await ctx.send("You can't steal from your own house, what're you, crazy??", delete_after=10)
            return
        if random.random() >= .60:
            points_changed = random.randint(30, 45)
            if random.random() >= .80:
                points_changed = random.randint(50, 60)
        else:
            points_changed = random.randint(-25, -15)
            if random.random() <= .40:
                points_changed = random.randint(-45, -25)
        steal_from = random.choice(Player.objects(house=house_name.capitalize()))
        Points(player=ctx.player, house=ctx.player.house, type="steal", points=points_changed, season=self.season).save()
        Points(player=steal_from, house=steal_from.house, type="steal", points=points_changed, season=self.season).save()
        emb = discord.Embed(title="Stealing", colour=int(ctx.player.emb_conf['color'], 16))
        chg = "gain" if points_changed > 0 else "lose"
        random_text = random.choice(RandomText.objects(type="steal", points=chg))
        emb.description = random_text.text.format(house=steal_from.house, points=abs(points_changed))
        if random_text.author != "":
            emb.set_footer(text=f"Phrase provided from: {random_text.author}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.command()
    async def beg(self, ctx):
        cur_timeout = Timeout.objects(player=ctx.player, reason="begging").first()
        if cur_timeout is None:
            cur_timeout = Timeout(player=ctx.player, reason="begging", until=str(arrow.now())).save()
        if arrow.now() >= arrow.get(cur_timeout.until):
            cur_timeout.update(until=str(arrow.now().shift(hours=6)))
        else:
            await ctx.send(
                "It seems you've begged a few too many times! You can beg again "
                f"{arrow.get(cur_timeout.until).humanize(arrow.now(), granularity=['hour', 'minute'])}.".replace(
                '0 hours and ', '').replace(' and 0 minutes', '').replace(' and 0 seconds', ''), delete_after=10)
            return
        if random.random() + ctx.player.rng_stats['beg'] <= .95:
            points_awarded = random.randint(40, 70)
            chg = "big"
            if random.random() + ctx.player.rng_stats['beg'] < 0.65:
                points_awarded = random.randint(25, 35)
                chg = "gain"
        else:
            Points(player=ctx.player, house=ctx.player.house, type="beg", points=150, season=self.season).save()
            emb = discord.Embed(title="**HOLY FUCKING SHIT!**", colour=int(ctx.player.emb_conf['color'], 16),
                                description="Your luck just fuckin' turned around, bucko."
                                            " You just gained {} points for {}.".format(
                                    150, ctx.player.house))
            emb.set_footer(text="From Dumbledore's Grace")
            return await ctx.send(embed=emb, delete_after=60)
        random_text = random.choice(RandomText.objects(type="beg", points=chg))
        Points(player=ctx.player, house=ctx.player.house, type="beg", points=points_awarded, season=self.season).save()
        emb = discord.Embed(
            title="Begging",
            colour=int(ctx.player.emb_conf['color'], 16),
            description=random_text.text.format(house=ctx.player.house, points=points_awarded)
        )
        if not random_text.author == "":
            emb.set_footer(text=f"Phrase provided from: {random_text.author}")
        await ctx.send(embed=emb, delete_after=60)

    @commands.command()
    async def daily(self, ctx):
        if (cur_timeout := Timeout.objects(player=ctx.player, reason="daily").first()) is None or arrow.now().naive > cur_timeout.until:
            payout = random.randint(100, 200)
            await ctx.send(f"Daily rewards are still a work in progress, but you get {payout} points!", delete_after=60)
            Points(player=ctx.player, house=ctx.player.house, type="daily", points=payout, season=self.season).save()
            Timeout.objects(player=ctx.player, reason="daily").upsert_one(set__until=arrow.now().shift(days=1).naive)
        else:
            await ctx.send("Sorry, you'll have to wait for your daily reward!", delete_after=20)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(aliases=['ps'])
    async def player_stats(self, ctx, player: typing.Optional[discord.User]):
        if player is not None:
            ctx.player = Player.objects(dis_id=player.id)
            data = [i.points for i in Points.objects(player=Player.objects(dis_id=str(player.id))[0])]
        else:
            data = [i.points for i in Points.objects(player=ctx.player)]
        cur_player_diffs = list(itertools.accumulate(data))
        plt.clf()
        plt.plot([float(i) for i in range(0, len(cur_player_diffs) + 1)],
                 [0] + [float(i) for i in list(cur_player_diffs)])
        plt.xticks([float(i) for i in range(0, len(cur_player_diffs) + 1)])
        plt.yticks([float(i) for i in range(0, (max(cur_player_diffs) // 10 * 10) + 10, 10)])
        plt.grid(True)
        plt.savefig("temp_fig.png")
        emb = discord.Embed(
            title=f"{ctx.player.name} Stats",
            description="X-Axis is the amount of bot commands\nY-Axis is the amount of points."
        )
        await ctx.send(embed=emb)
        await ctx.send(file=discord.File("temp_fig.png"))
        os.remove("temp_fig.png")

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if channel.name != "general":
            return
        p = await channel.pins()
        if len(p) >= 45:
            awarded = 50 + ((50 - len(p)) * 20)
            awarder = 20 + ((50 - len(p)) * 10)
        else:
            awarded = 50
            awarder = 20
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.message_pin, limit=1):
            t = arrow.now().naive - entry.created_at
            if t.seconds == 0 or t.days < 0:
                giver = Player.objects(dis_id=str(entry.user.id)).first()
                given = Player.objects(dis_id=str(entry.target.id)).first()
                if giver.house != given.house:
                    await channel.send(f"{awarded} points to {given.house}!")
                    await channel.send(f"(And {awarder} for {giver.house} for finding such a spicy maymay ;))",
                                       delete_after=10)
                    Points(player=given, house=given.house, type="pinee", points=50, season=self.season).save()
                else:
                    await channel.send(f"{awarder} points for {given['house']}!")
                    await channel.send(f"Circlejerking has officially been nerfed.", delete_after=5)
                Points(player=giver, house=giver.house, type="pinner", points=20, season=self.season).save()
        if len(p) == 50:
            self.season_helper()
            await self.client.invoke(self.client.get_command("archive_pins"))
            await channel.send("Season is over! Automagically starting new season. ;)")

    async def cog_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            await ctx.send(
                f"You're a little tired from your last fiasco. "
                f"Wait {round(error.retry_after, 2)} seconds to try again.", delete_after=10)
        else:
            await ctx.send(f"Something went wrong, but i'm not quite sure what. <@!{self.client.owner_id}>\n{sys.exc_info()}")
            sentry_sdk.capture_exception(error)
            raise error


def setup(client):
    client.add_cog(PointsCog(client))
