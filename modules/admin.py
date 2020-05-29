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
        a_filter = ["a", "à", "á", "â", "ä", "æ", "ã", "å", "ā"]
        n_filter = ["n", "ñ", "ń"]
        i_filter = ["i", "î", "ï", "í", "ī", "į", "ì"]
        e_filter = ["e", "è", "é", "ê", "ë", "ē", "ė", "ę"]

        string = "nigga"

        n_filtered = []
        a_filtered = []
        i_filtered = []
        for n in n_filter:
            n_filtered.append(string.replace("n", n))
        for item in n_filtered:
            for a in a_filter:
                a_filtered.append(item.replace("a", a))
        for item in a_filtered:
            for i in i_filter:
                i_filtered.append(item.replace("i", i))

        first_filtered = i_filtered

        string = "nigger"

        n_filtered = []
        a_filtered = []
        i_filtered = []
        e_filtered = []
        for n in n_filter:
            n_filtered.append(string.replace("n", n))
        for item in n_filtered:
            for a in a_filter:
                a_filtered.append(item.replace("a", a))
        for item in a_filtered:
            for i in i_filter:
                i_filtered.append(item.replace("i", i))
        for item in i_filtered:
            for e in e_filter:
                e_filtered.append(item.replace("e", e))

        second_filtered = e_filtered

        big_bad_list = []
        big_bad_list.extend(first_filtered)
        big_bad_list.extend(second_filtered)

        message = message.replace(" ", "")
        if any(bad in message for bad in big_bad_list):
            return True
        else:
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
