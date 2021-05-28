import inspect
import contextlib
import io
from discord.ext import commands


class AdminCog(commands.Cog, name="Admin"):
    def __init__(self, client):
        self.client = client
        self.description = "This module is meant to be used by the owner of the bot."
        self.tonys_a_cunt = [
            "\u0628",
            "\u064d",
            "\u0631",
        ]

    @commands.command(name="run", hidden=True,
                      help="Executes Python code from Discord on the bot.\n"
                           "(Can be dangerous, reserved for only the owner)",
                      brief="Executes Python code.",
                      usage="```py <code> ```")
    @commands.is_owner()
    async def run(self, ctx, *, code):
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

    @commands.command(name='load', hidden=True, help="Loads a cog into the bot to extend bot functionality.",
                      brief="Loads a cog.")
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module."""
        try:
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been loaded!", delete_after=5)

    @commands.command(name='unload', hidden=True, help="Unloads a cog from the bot.", brief="Unloads a cog.")
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module."""
        try:
            if cog == "modules.admin":
                await ctx.send("It's not recommended to unload the admin cog.", delete_after=5)
                return
            self.client.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`**\n {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been unloaded!", delete_after=5)

    @commands.command(name='reload', hidden=True,
                      help="Reloads a cog into the bot.\nUseful for when updating the cogs separate from the bot.",
                      brief="Reloads a cog.")
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module."""
        try:
            self.client.unload_extension(cog)
            self.client.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f"`{cog}` has been reloaded!", delete_after=5)

    @commands.Cog.listener()
    async def on_message(self, message):
        if any(bad in message.content for bad in self.tonys_a_cunt):
            await message.delete()
            dmchannel = await message.author.create_dm()
            await dmchannel.send("You're a cunt for trying that.")
            return


def setup(client):
    client.add_cog(AdminCog(client))
