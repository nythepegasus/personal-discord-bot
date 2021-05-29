import asyncio
import string
import typing
import discord
import reactionmenu as rm
from discord.ext import commands
from fuzzywuzzy import fuzz, process
from more_itertools import chunked
from utils.schema import Phrase, PhraseCount, Player, RandomText


class PhrasesCog(commands.Cog, name="Phrases"):
    def __init__(self, client):
        self.client = client
        self.description = "This module adds phrases tracking, random phrases for Points Module, along with other things."

    def word_check(self, msg):
        rslur = ["retard", "r*tard", "ret*rd"]
        nslur = ["nigger", "n*gger", "nigga", "n*gga"]
        chks = process.extract(msg.lower(), nslur, scorer=fuzz.token_sort_ratio) + process.extract(msg.lower(), rslur,
                                                                                                   scorer=fuzz.token_sort_ratio)
        chks.sort(key=lambda x: x[1], reverse=True)
        for w in chks:
            if w[1] > 90:
                return (chks, True)
        return (chks, False)

    async def checker(self, msg: discord.Message, check_func, timeout: int = 30) -> typing.Union[
        discord.Reaction, None]:
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=timeout, check=check_func)
            await msg.remove_reaction(emoji=reaction, member=user)
            return reaction
        except asyncio.TimeoutError:
            return None

    @commands.command(name="add_phrase", aliases=["ap"])
    async def add_phrase(self, ctx, phrase):
        exists = True if Phrase.objects(phrase=phrase).first() is not None else False
        if exists:
            return await ctx.send("Phrase already exists!", delete_after=7)
        elif len(phrase) < 3:
            return await ctx.send("Phrase too short!", delete_after=7)
        elif len(phrase) > 35:
            return await ctx.send("Phrase too long!", delete_after=7)
        elif self.word_check(phrase)[1]:
            return await ctx.send("Phrase cannot be approved!", delete_after=7)
        Phrase(phrase=phrase, adder=ctx.author.name).save()
        await ctx.send("Phrase added!", delete_after=10)

    @commands.command(name="remove_phrase", aliases=["rp"])
    async def remove_phrase(self, ctx, phrase):
        Phrase.objects(phrase=phrase).delete()
        await ctx.send("Removed phrase!", delete_after=10)

    @commands.command(name="phrase_counts", aliases=["pc"])
    async def phrase_counts(self, ctx):
        menu = rm.ReactionMenu(ctx, name="Phrase Counts", back_button='◀️', next_button='▶️',
                               config=rm.ReactionMenu.DYNAMIC, rows_requested=5)
        for phrase in Phrase.objects:
            menu.add_row(f"{phrase.phrase}: {sum(p.times for p in PhraseCount.objects(phrase=phrase))}\n")
        await menu.start()
        await asyncio.sleep(60)
        await menu.stop(delete_menu_message=True)

    @commands.command(aliases=['arp'])
    async def add_rphrase(self, ctx: discord.Message):
        types = {'1️⃣': "spell", '2️⃣': "steal", '3️⃣': "beg"}
        gl = {'1️⃣': "win", '2️⃣': "lose", ":beg_two:": "big win"}

        def type_emb_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '❌']

        def gl_emb_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '❌']

        def msg_check(msg: discord.Message):
            return msg.author == ctx.author

        type_emb = discord.Embed(title="Choose Type of Phrase", colour=0x3b88c3)
        type_emb.add_field(name="1️⃣ Spell\n\n2️⃣ Steal\n\n3️⃣ Beg", value="\u200b", inline=False)
        gl_emb = discord.Embed(title="Choose Points", colour=0x3b88c3)
        user_msg = await ctx.send(embed=type_emb)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "❌"]:
            await user_msg.add_reaction(emoji=emoji)

        react = await self.checker(user_msg, type_emb_check)

        if not react:
            await user_msg.delete()
            return await ctx.send("Reaction timeout reached!", delete_after=7)
        elif str(react.emoji) == "❌":
            await user_msg.delete()
            return await ctx.send("Process cancelled by user!", delete_after=7)
        elif str(react.emoji) == "3️⃣":
            gl_emb.add_field(name="1️⃣ Win\n\n2️⃣ Big Win", value="\u200b", inline=False)
        else:
            gl_emb.add_field(name="1️⃣ Win\n\n2️⃣ Lose", value="\u200b", inline=False)

        await user_msg.edit(embed=gl_emb)

        await user_msg.clear_reaction(emoji="3️⃣")
        react2 = await self.checker(user_msg, gl_emb_check)

        await user_msg.delete()
        if not react2:
            return await ctx.send("Reaction timeout reached!", delete_after=7)
        elif str(react2.emoji) == "❌":
            return await ctx.send("Process cancelled by user!", delete_after=7)

        t = await ctx.send(content="```Please input your phrase with {house} and {points} included!```")

        msg = await self.client.wait_for('message', timeout=90, check=msg_check)
        text = msg.content

        await t.delete()
        if "{house}" not in msg.content and "{points}" not in msg.content:
            return await ctx.send("Your message must contain {house} and {points}!", delete_after=7)

        author_check = await ctx.send(
            embed=discord.Embed(title="Do you want to add an author?", description="React with yes or no to choose."))

        [await author_check.add_reaction(emoji=emoji) for emoji in ["✅", "❌"]]

        author_react = await self.checker(author_check,
                                   lambda reaction, user: user == ctx.author and str(reaction.emoji) in ["✅", "❌"])

        await author_check.delete()
        if author_react is None or str(author_react.emoji) == "❌":
            author = ""
        else:
            try:
                t = await ctx.send("```Type out the author```")
                author_msg = await self.client.wait_for('message', timeout=60, check=msg_check)
                author = author_msg.content
                await t.delete()
                await author_msg.delete()
            except asyncio.TimeoutError:
                await ctx.send("Author input timed out.\nUsing blank author", delete_after=7)
                author = ""

        RandomText(type=types[str(react.emoji)],
                   points=gl[":beg_two:"] if str(react.emoji) == "3️⃣" and str(react2.emoji) == "2️⃣"
                   else gl[str(react2.emoji)],
                   text=text,
                   author=author,
                   queue=True).save()

        await msg.delete()

        await ctx.send("Phrase added to queue, hopefully you'll see it soon! ;)", delete_after=10)

    @commands.command(aliases=["apprp"])
    async def approve_rphrases(self, ctx: discord.Message):
        queued_phrases = list(RandomText.objects(queue=True))
        if not queued_phrases:
            return await ctx.send("No messages in queue!", delete_after=7)

        def embed_gen(queued_phrases):
            return [discord.Embed(title="Approve Phrases", colour=0xffffff).add_field(name="Queue", value="".join(
            [f"{list(queued_phrases).index(p) + 1} {p.text} | Type: {p.type} | Points: {p.points} | Author: {p.author}\n\n"
             for p in rp])) for rp in chunked(queued_phrases, 4)]

        index = 0
        embed_pages = embed_gen(queued_phrases)
        menu = await ctx.send(embed=embed_pages[index])
        for emoji in ['✅', '❌', '🚫', '◀️', '▶️']:
            await menu.add_reaction(emoji=emoji)
        while True:
            react = await self.checker(menu,
                                       lambda reaction, user: user == ctx.author and
                                                              str(reaction.emoji) in ['◀️', '▶️', '✅', '❌', '🚫'])
            if react is None or str(react.emoji) == '🚫':
                await menu.delete()
                await ctx.send("Random phrases have been updated!", delete_after=10)
                break
            elif str(react.emoji) == '▶️':
                if index == len(embed_pages) - 1:
                    index = 0
                else:
                    index += 1
                await menu.edit(embed=embed_pages[index])
            elif str(react.emoji) == '◀️':
                if index == 0:
                    index = len(embed_pages) - 1
                else:
                    index -= 1
                await menu.edit(embed=embed_pages[index])
            elif str(react.emoji) == '✅' or str(react.emoji) == '❌':
                if str(embed_pages[index].colour) == "#ffffff":
                    [await menu.clear_reaction(emoji=emoji) for emoji in ['◀️', '▶️']]
                    if str(react.emoji) == '✅':
                        embed_pages[index].title = "Approve which?"
                        embed_pages[index].colour = 0x00BA00
                    else:
                        embed_pages[index].title = "Disapprove which?"
                        embed_pages[index].colour = 0xFF0000
                    await menu.edit(embed=embed_pages[index])
                    try:
                        msg = await self.client.wait_for('message', timeout=60,
                                                         check=lambda msg: msg.author == ctx.author)
                        int(msg.content)
                    except ValueError:
                        await ctx.send("Make sure to choose a number!", delete_after=5)
                        continue
                    if int(msg.content) <= len(queued_phrases):
                        try:
                            if str(react.emoji) == '✅':
                                list(queued_phrases)[int(msg.content) - 1].update(queue=False)
                            else:
                                list(queued_phrases)[int(msg.content) - 1].delete()
                            queued_phrases = RandomText.objects(queue=True)
                            embed_pages = embed_gen(queued_phrases)
                        except IndexError:
                            await ctx.send("Make sure to choose a numbered item!", delete_after=5)
                    await msg.delete()
                [await menu.add_reaction(emoji=emoji) for emoji in ['◀️', '▶️']]
                try:
                    embed_pages[index].title = "Approve Phrases"
                    embed_pages[index].colour = 0xFFFFFF
                except IndexError:
                    index = 0
                    await menu.edit(embed=embed_pages[index])
                await menu.edit(embed=embed_pages[index])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == 379105703840841739 and "piss report" in message.content:
            await message.add_reaction(emoji="👍")
            return await message.reply("Nice piss report, bro.")
        if message.author.id == 546074324134658049 and message.content.lower().startswith("yeah?"):
            suicide = self.client.get_emoji(848332621020528651)
            return await message.add_reaction(emoji=suicide)
        if message.author == self.client.user or message.content.startswith("buh!"):
            return
        elif not any(char in message.content for char in list(string.ascii_letters)):
            return
        elif self.word_check(message.content)[1]:
            return await message.delete()
        for phrase in Phrase.objects:
            if phrase.phrase in message.content:
                PhraseCount.objects(phrase=phrase).upsert_one(inc__times=1,
                                                              set__phrase=phrase,
                                                              set__said=Player.objects(
                                                                  dis_id=str(message.author.id)).first()
                                                              )


def setup(client):
    client.add_cog(PhrasesCog(client))
