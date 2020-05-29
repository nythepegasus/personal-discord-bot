import re
from discord.ext import commands


class AdminCog(commands.Cog, name="Admin Commands"):
    def __init__(self, client):
        self.client = client
        self.tonys_a_cunt = [
            "\u0628",
            "\u064d",
            "\u0631",
        ]

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module."""
        try:
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been loaded!")

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module."""
        try:
            if cog == "modules.admin":
                await ctx.send("It's not recommended to unload the admin cog.")
                return
            self.client.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been unloaded!")

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module."""
        try:
            self.client.unload_extension(cog)
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been reloaded!")

    def filter_message(self, message):
        message = message.replace(" ", "")
        regexes = [  # Probably use this as a config list in a json file
            r"(n|ñ|ń)+.*(i|î|ï|í|ī|ī|į|ì)+.*g+.*(a|à|á|â|ä|æ|ã|å|ā)*.*",
            r"(n|ñ|ń)+.*(i|î|ï|í|ī|ī|į|ì)+.*g+.*(e|è|é|ê|ë|ē|ė|ę)*.*r*.*"
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
        if any(bad in message.content for bad in self.tonys_a_cunt) or self.filter_message(message.content):
            await message.delete()
            dmchannel = await message.author.create_dm()
            await dmchannel.send("You're a cunt for trying that.")
            return


def setup(client):
    client.add_cog(AdminCog(client))
