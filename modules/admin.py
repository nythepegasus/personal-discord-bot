import re
import discord
import inspect
import contextlib
import io
import sentry_sdk
import json
from discord.ext import commands

sentry_sdk.init(
    json.load(open("conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)


class AdminCog(commands.Cog, name="Admin Commands"):
    def __init__(self, client):
        self.client = client
        self.tonys_a_cunt = [
            "\u0628",
            "\u064d",
            "\u0631",
        ]

    @commands.command(name="run", hidden=True)
    @commands.is_owner()
    async def run(self, ctx, *, code):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        code = code.replace('```py', '')
        code = code.replace('```', '')
        python = '```py\n{}\n```'
        result = None
        env = {
            'client': self.client,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }
        env.update(globals())
        str_obj = io.StringIO()  # Retrieves a stream of data
        try:
            with contextlib.redirect_stdout(str_obj):
                result = exec(code, env)
                if inspect.isawaitable(result):
                    await result
                    return
        except Exception as e:
            return await ctx.send(f"```{e.__class__.__name__}: {e}```")
        if str_obj.getvalue() != "":
            await ctx.send(f'```{str_obj.getvalue()}```')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        """Command which Loads a Module."""
        try:
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            msg = await ctx.send(f"`{cog}` has been loaded!")
            await msg.delete(delay=5)

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            print(isinstance(ctx.channel, discord.channel.DMChannel))
            await ctx.message.delete()
        """Command which Unloads a Module."""
        try:
            if cog == "modules.admin":
                msg = await ctx.send("It's not recommended to unload the admin cog.")
                await msg.delete(delay=5)
                return
            self.client.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            msg = await ctx.send(f"`{cog}` has been unloaded!")
            await msg.delete(delay=5)

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        """Command which Reloads a Module."""
        try:
            self.client.unload_extension(cog)
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            msg = await ctx.send(f"`{cog}` has been reloaded!")
            await msg.delete(delay=5)

    def filter_message(self, message):
        message = message.replace(" ", "")
        regexes = [  # Probably use this as a config list in a json file
            r"(n|ñ|ń)+.*(i|î|ï|í|ī|ī|į|ì)+.*g{2,}.*(a|à|á|â|ä|æ|ã|å|ā)*.*",
            r"(n|ñ|ń)+.*(i|î|ï|í|ī|ī|į|ì)+.*g{2,}.*(e|è|é|ê|ë|ē|ė|ę)*.*r*.*"
        ]
        for reg in regexes:
            matches = re.finditer(reg, message, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                test = matchNum
            try:
                tester = test
                print("Bad stuff afloat!")
                return True
                break
            except NameError:
                print("Nothing bad here!")
                return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if any(bad in message.content for bad in self.tonys_a_cunt):
            await message.delete()
            dmchannel = await message.author.create_dm()
            await dmchannel.send("You're a cunt for trying that.")
            return


def setup(client):
    client.add_cog(AdminCog(client))
