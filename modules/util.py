import asyncio
import datetime
import discord
import json
import psutil
import sentry_sdk
import logging
import speedtest
import time
import uptime
from discord.ext import commands
import pushover

sentry_sdk.init(
    json.load(open("conf_files/conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)


class UtilCog(commands.Cog, name="Utility Commands"):
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger("UtilCog")
        self.logger.setLevel(logging.DEBUG)
        a_handler = logging.FileHandler("logs/util.log")
        a_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - $(message)s"))
        a_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(a_handler)

    async def cog_before_invoke(self, ctx):
        self.logger.info(f"{ctx.author.name} ran {ctx.command} with message {ctx.message.content}")

    @commands.command(aliases=["h"])
    async def help(self, ctx):
        help_emb = discord.Embed(title="Bot Commands", colour=0x00adff)
        help_emb.add_field(name="buh!add_phrase | buh!ap", value="Add phrase to the tracker", inline=False)
        help_emb.add_field(name="buh!remove_phrase | buh!rp", value="Remove phrase from the tracker", inline=False)
        help_emb.add_field(name="buh!phrases_counts | buh!pc", value="Check phrases on the tracker", inline=False)
        help_emb.add_field(name="buh!archive_pins | buh!arcp", value="Archive all pins from #general chat",
                           inline=False)
        help_emb.add_field(name="buh!house_points | buh!hp", value="Check each house's points.", inline=False)
        help_emb.add_field(name="buh!cast_spell | buh!cs",
                           value="Gamble your house's points away, and see where fate takes you.", inline=False)
        help_emb.add_field(name="buh!stats", value="Check the discord bot's current server stats", inline=False)
        help_emb.add_field(name="buh!netstats", value="Check the discord bot's current net stats", inline=False)
        help_emb.add_field(name="More to come!", value=":3", inline=False)
        help_emb.set_footer(text="Developed by Nikki")
        await ctx.send(embed=help_emb)

    @commands.command(name="archive_pins", aliases=["arcp"])
    @commands.is_owner()
    async def archive_pins(self, ctx):
        guild = self.client.guilds[0]
        for channel in guild.channels:
            if channel.name == "general":
                general_chat = channel
            if channel.name == "archived-pins":
                archive_channel = channel
        myPins = await general_chat.pins()
        if len(myPins) == 50:
            conf_data = json.load(open("db_files/points.json"))
            json.dump(conf_data, open("db_files/points.json", "w"), indent=4)
        elif len(myPins) == 0:
            await ctx.send("No more pins")
            return
        for pin in myPins:
            emb = discord.Embed(
                description=pin.content,
                timestamp=datetime.datetime.utcfromtimestamp(int(time.time())),
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
                    emb.set_footer(text=f"Part 1 | Archived from #{pin.channel} | {pin.jump_url}")
                    await archive_channel.send(embed=emb)
                    attach_counter = 1
                    try:
                        for attachment in pin.attachments:
                            next_emb = discord.Embed(
                                timestamp=datetime.datetime.utcfromtimestamp(int(time.time())),
                            )
                            next_emb.set_author(
                                name=pin.author,
                                icon_url=pin.author.avatar_url,
                                url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                                    pin.guild.id, pin.channel.id, pin.id)
                            )
                            img_url = pin.attachments[attach_counter].url
                            next_emb.set_image(url=img_url)
                            next_emb.set_footer(text=f"Part {attach_counter + 1} | Archived from #{pin.channel}")
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

    @commands.command()
    async def stats(self, ctx):
        cur_uptime = time.gmtime(uptime.uptime())
        stat_emb = discord.Embed(title="Discord Bot's Server Stats", colour=0x00adff)
        stat_emb.add_field(name="Current Uptime",
                           value=f"{cur_uptime.tm_yday - 1}:{cur_uptime.tm_hour}:{str(cur_uptime.tm_min).zfill(2)}")
        stat_emb.add_field(name="RAM Percentage", value=psutil.virtual_memory()[2])
        stat_emb.add_field(name="CPU Percentage", value=psutil.cpu_percent())
        stat_emb.set_footer(text="Proudly fixed with nano.")
        await ctx.send(embed=stat_emb)

    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.command()
    async def netstats(self, ctx):
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
    async def netstats_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Wait {round(error.retry_after, 2)} more seconds.", delete_after=5)
        else:
            raise error

    @commands.cooldown(1, 15)
    @commands.command()
    async def feature_request(self, ctx, *, suggestion):
        json_data = json.load(open(self.client.conf_file))
        pshovr = pushover.Client(user_key=json_data['pushover']['user_key'],
                                 api_token=json_data['pushover']['api_key'])
        pshovr.send(pushover.Message(suggestion, title="Discord Suggestion!"))
        await ctx.send(
            "Your feature has been suggested, " + self.client.owner.mention + " will (probably) get to work on it soon!",
            delete_after=10)


def setup(client):
    client.add_cog(UtilCog(client))
