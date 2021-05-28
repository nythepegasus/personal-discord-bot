import arrow
import discord
import psutil
import speedtest
import time
import uptime
from discord.ext import commands


class UtilCog(commands.Cog, name="Utility"):
    def __init__(self, client):
        self.client = client
        self.description = "This module adds various utility functions."

    @commands.command(aliases=["h"])
    async def help(self, ctx, query=None):
        if query is not None:
            com = self.client.get_command(query.lower())
            cog = self.client.get_cog(query.capitalize())
            if com:
                help_emb = discord.Embed(title=com.name, description=com.help)
                help_emb.set_footer(text=f"Command provided by {self.client.user.display_name}")
                return await ctx.send(embed=help_emb, delete_after=20)
            elif cog:
                help_emb = discord.Embed(title=cog.qualified_name, description=cog.description)
                for command in cog.get_commands():
                    help_emb.add_field(name=command.name, value=command.brief, inline=False)
                help_emb.set_footer(text=f"Cog provided by {self.client.user.display_name}")
                return await ctx.send(embed=help_emb, delete_after=20)
            else:
                help_emb = discord.Embed(title="Error! Unknown query.", description=f"{query} is not a known command or cog!")
                help_emb.set_footer(text=f"For more help, type {self.client.command_prefix}help")
                await ctx.send(embed=help_emb, delete_after=30)
        else:
            help_emb = discord.Embed(title=f"{self.client.user.display_name}'s Cogs")
            for cog in self.client.cogs:
                description = self.client.cogs[cog].description
                help_emb.add_field(name=cog, value=description if len(description) != 0 else f"{cog} adds commands!")
            help_emb.set_footer(text=f"For more help on a cog or command, type {self.client.command_prefix}help <query>")
            return await ctx.send(embed=help_emb, delete_after=20)

    @commands.is_owner()
    @commands.command(name="archive_pins", aliases=["arcp"])
    async def archive_pins(self, ctx):
        """Archives the pins in #general into #archived-pins"""
        general_chat = discord.utils.get(ctx.guild.channels, name="general")
        archive_channel = discord.utils.get(ctx.guild.channels, name="archived-pins")
        myPins = await general_chat.pins()
        if len(myPins) == 0:
            await ctx.send("No more pins")
            return
        for pin in myPins:
            if pin.attachments:
                for attachment in pin.attachments:
                    next_emb = discord.Embed(description=pin.content, timestamp=arrow.now())
                    next_emb.set_author(name=pin.author,
                                        icon_url=pin.author.avatar_url,
                                        url=f"https://discord.com/channels/{pin.guild.id}/{pin.channel.id}/{pin.id}")
                    next_emb.set_image(url=attachment.url)
                    next_emb.set_footer(text=f"Part {pin.attachments.index(attachment) + 1} | Archived from #{pin.channel}")
                    await archive_channel.send(embed=next_emb)
            else:
                emb = discord.Embed(
                    description=pin.content,
                    timestamp=arrow.now(),
                )
                emb.set_author(
                    name=pin.author,
                    icon_url=pin.author.avatar_url,
                    url=f"https://discord.com/channels/{pin.guild.id}/{pin.channel.id}/{pin.id}"
                )
                emb.set_footer(text=f"Archived from #{pin.channel}")
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


def setup(client):
    client.add_cog(UtilCog(client))
