import asyncio
import json
import discord
import sentry_sdk
import logging
from discord.ext import commands, tasks

sentry_sdk.init(
    json.load(open("conf_files/conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)


class AmongUsCog(commands.Cog, name="Among Us Cog"):
    def __init__(self, client):
        self.client = client
        self.vc = None
        self.voting_time = None
        self.client.au_db_file = "db_files/amongus.json"
        self.logger = logging.getLogger("AmongUsCog")
        self.logger.setLevel(logging.DEBUG)
        a_handler = logging.FileHandler("logs/amongus.log")
        a_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        a_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(a_handler)

    async def cog_before_invoke(self, ctx):
        # self.logger.info(f"{ctx.author.name} ran {ctx.command} with message {ctx.message.content}")
        pass

    @tasks.loop(seconds=1)
    async def during_game(self):
        players = json.load(open(self.client.au_db_file))
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
                json.dump(players, open(self.client.au_db_file, "w"), indent=4)
        else:
            for u in self.vc.members:
                if u.id in players["alive"]:
                    await u.edit(mute=True, deafen=True)
                if u.id in players["dead"]:
                    await u.edit(mute=False, deafen=False)


    @commands.command(name="during_round", aliases=["dr"])
    async def during_round(self, ctx):
        players = json.load(open(self.client.au_db_file))
        players["voting"] = False
        json.dump(players, open(self.client.au_db_file, "w"), indent=4)

    @commands.command(name="during_voting", aliases=["dv"])
    async def during_voting(self, ctx):
        players = json.load(open(self.client.au_db_file))
        players["voting"] = True
        json.dump(players, open(self.client.au_db_file, "w"), indent=4)

    @commands.command(name="start_game", aliases=["sg"])
    async def start_game(self, ctx):
        #self.voting_time = int(voting_time)
        self.vc = ctx.message.author.voice.channel
        reset_str = {"voting": False, "alive": [],"dead": [],"all_players": []}
        json.dump(reset_str, open(self.client.au_db_file, "w"), indent=4)
        players = json.load(open(self.client.au_db_file))
        for u in self.vc.members:
            if u.bot:
                pass
            else:
                players["alive"].append(u.id)
                players["all_players"].append(u.id)
        json.dump(players, open(self.client.au_db_file, "w"), indent=4)
        self.during_game.start()

    @commands.command(name="end_game", aliases=["eg"])
    async def end_game(self, ctx):
        server = self.client.guilds[0]
        players = json.load(open(self.client.au_db_file))
        for u in self.vc.members:
            await u.edit(deafen=False, mute=False)
        self.during_game.cancel()

    @commands.command(name="pdied", aliases=["pd"])
    async def pdied(self, ctx, player: discord.Member):
        players = json.load(open(self.client.au_db_file))
        players["alive"].remove(player.id)
        players["dead"].append(player.id)
        json.dump(players, open(self.client.au_db_file, "w"), indent=4)

    async def cog_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, discord.HTTPException):
            return await ctx.send("Player is not in the correct VC anymore!\nCannot perform actions on them.")
        else:
            return await ctx.send(f"Something went wrong!\n{error}")


def setup(client):
    client.add_cog(AmongUsCog(client))