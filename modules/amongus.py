import asyncio
import json
import discord
from discord.ext import commands, tasks


class AmongUsCog(commands.Cog, name="Among Us Cog"):
    def __init__(self, client):
        self.client = client
        self.vc = None
        self.voting_time = None
        self.db_file = "db_files/amongus.json"

    @tasks.loop(seconds=1)
    async def during_game(self):
        players = json.load(open(self.db_file))
        server = self.client.guilds[0]
        if players["voting"]:
            for u in self.vc.members:
                await u.edit(deafen=False)
                if u.id in players["alive"]:
                    await u.edit(mute=False)
                elif u.id in players["dead"]:
                    await u.edit(mute=True)
            if self.voting_time:
                await asyncio.sleep(self.voting_time+2)
                players["voting"] = False
                json.dump(players, open(self.db_file, "w"), indent=4)
        else:
            for u in self.vc.members:
                if u.id in players["alive"]:
                    await u.edit(mute=True, deafen=True)
                if u.id in players["dead"]:
                    await u.edit(mute=False, deafen=False)


    @commands.command(name="during_round", aliases=["dr"])
    async def during_round(self, ctx):
        players = json.load(open(self.db_file))
        players["voting"] = False
        json.dump(players, open(self.db_file, "w"), indent=4)
        if not isinstance(ctx.channel, discord.DMChannel) or not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.delete()

    @commands.command(name="during_voting", aliases=["dv"])
    async def during_voting(self, ctx):
        players = json.load(open(self.db_file))
        players["voting"] = True
        json.dump(players, open(self.db_file, "w"), indent=4)
        if not isinstance(ctx.channel, discord.DMChannel) or not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.delete()

    @commands.command(name="start_game", aliases=["sg"])
    async def start_game(self, ctx):
        #self.voting_time = int(voting_time)
        self.vc = ctx.message.author.voice.channel
        reset_str = {"voting": False, "alive": [],"dead": [],"all_players": []}
        json.dump(reset_str, open(self.db_file, "w"), indent=4)
        players = json.load(open(self.db_file))
        for u in self.vc.members:
            if u.bot:
                pass
            else:
                players["alive"].append(u.id)
                players["all_players"].append(u.id)
        json.dump(players, open(self.db_file, "w"), indent=4)
        self.during_game.start()
        if not isinstance(ctx.channel, discord.DMChannel) or not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.delete()

    @commands.command(name="end_game", aliases=["eg"])
    async def end_game(self, ctx):
        server = self.client.guilds[0]
        players = json.load(open(self.db_file))
        for u in self.vc.members:
            await u.edit(deafen=False, mute=False)
        self.during_game.cancel()
        if not isinstance(ctx.channel, discord.DMChannel) or not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.delete()

    @commands.command(name="pdied", aliases=["pd"])
    async def pdied(self, ctx, player: discord.Member):
        players = json.load(open(self.db_file))
        players["alive"].remove(player.id)
        players["dead"].append(player.id)
        json.dump(players, open(self.db_file, "w"), indent=4)
        if not isinstance(ctx.channel, discord.DMChannel) or not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.delete()

    async def cog_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, discord.HTTPException):
            return await ctx.send("Player is not in the correct VC anymore!\nCannot perform actions on them.")
        else:
            return await ctx.send(f"Something went wrong!\n{error}")


def setup(client):
    client.add_cog(AmongUsCog(client))