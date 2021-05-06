import asyncio
import typing
import discord
import json
import sentry_sdk
import reactionmenu as rm
from fuzzywuzzy import fuzz, process
from discord.ext import commands


class PhrasesCog(commands.Cog, name="phrases"):
    def __init__(self, client):
        self.client = client
        self.client.phr_db_file = "db_files/phrases.json"

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

    async def checker(self, msg: discord.Message, check_func, timeout: int = 30) -> typing.Union[discord.Reaction, None]:
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=timeout, check=check_func)
            await msg.remove_reaction(emoji=reaction, member=user)
            return reaction
        except asyncio.TimeoutError:
            return None

    @commands.command(name="add_phrase", aliases=["ap"])
    async def add_phrase(self, ctx, phrase):
        data = json.load(open(self.client.phr_db_file))
        try:
            cur_index = data["phrases"][-1]["uid"] + 1
        except IndexError:
            cur_index = 1
        for line in data["phrases"]:
            if phrase == line["phrase"]:
                await ctx.send("Phrase already exists!", delete_after=5)
                return
            elif len(phrase) <= 2:
                await ctx.send("Phrase too short!", delete_after=5)
                return
            elif len(phrase) >= 35:
                await ctx.send("Phrase too long!", delete_after=5)
                return
            elif self.word_check(phrase)[1]:
                await ctx.send("You're a cunt!", delete_after=5)
                return
        add_phrase = {
            "uid": cur_index,
            "phrase": phrase,
            "times_said": 0,
        }
        with open(self.client.phr_db_file, "w") as f:
            data["phrases"].append(add_phrase)
            f.write(json.dumps(data, indent=4))
            await ctx.send("Phrase added!", delete_after=5)

    def update_phrase(self, phrase):
        data = json.load(open(self.client.phr_db_file))
        for d in data["phrases"]:
            if d.get("phrase").lower() in phrase.lower():
                d["times_said"] += 1
        with open(self.client.phr_db_file, "w") as f:
            f.write(json.dumps(data, indent=4))
            return "Updated phrase!"

    @commands.command(name="remove_phrase", aliases=["rp"])
    async def remove_phrase(self, ctx, phrase):
        data = json.load(open(self.client.phr_db_file))
        with open(self.client.phr_db_file, "w") as f:
            data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
            f.write(json.dumps(data, indent=4))
            await ctx.send("Removed phrase!", delete_after=5)

    @commands.command(name="phrase_counts", aliases=["pc"])
    async def phrase_counts(self, ctx):
        data = json.load(open(self.client.phr_db_file))
        menu = rm.ReactionMenu(ctx, name="Phrase Counts", back_button='◀️', next_button='▶️', config=rm.ReactionMenu.DYNAMIC, rows_requested=5)
        for phrase in data["phrases"]:
            menu.add_row(f"{phrase['phrase']}: {phrase['times_said']}\n")
        await menu.start()
        await asyncio.sleep(60)
        await menu.stop(delete_menu_message=True)

    @commands.command(aliases=['arp'])
    async def add_rphrase(self, ctx: discord.Message):
        json_data = json.load(open(self.client.random_phrases))
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
        await user_msg.add_reaction(emoji='1️⃣')
        await user_msg.add_reaction(emoji="2️⃣")
        await user_msg.add_reaction(emoji="3️⃣")
        await user_msg.add_reaction(emoji="❌")

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

        if not react2:
            await user_msg.delete()
            return await ctx.send("Reaction timeout reached!", delete_after=7)
        elif str(react2.emoji) == "❌":
            await user_msg.delete()
            return await ctx.send("Process cancelled by user!", delete_after=7)

        await user_msg.delete()
        t = await ctx.send(content="```Please input your phrase with {house} and {points} included!```")

        msg = await self.client.wait_for('message', timeout=60, check=msg_check)

        if "{house}" not in msg.content and "{points}" not in msg.content:
            await t.delete()
            return await ctx.send("Your message must contain {house} and {points}!", delete_after=7)

        phrase_to_add = {
            'type': types[str(react.emoji)],
            'points': gl[":beg_two:"] if str(react.emoji) == "3️⃣" and str(react2.emoji) == "2️⃣" else gl[str(react2.emoji)],
            'text': msg.content,
            'author': ctx.author.nick or ctx.author.name,
            'pos': len(json_data['queue'])
        }

        await t.delete()

        json_data["queue"].append(phrase_to_add)
        json.dump(json_data, open(self.client.random_phrases, 'w'), indent=4)
        await ctx.send("Phrase added to queue, hopefully you'll see it soon! ;)", delete_after=10)

    @commands.command(aliases=["apprp"])
    async def approve_rphrases(self, ctx: discord.Message):
        json_data = json.load(open(self.client.random_phrases))
        if len(json_data['queue']) == 0:
            return await ctx.send("No messages in queue!", delete_after=7)

        def re_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️', '✅', '🚫', '❌']

        def msg_check(msg: discord.Message):
            return msg.author == ctx.author

        def gen_menu(json_data):
            random_phrases = [json_data['queue'][i:i + 4] for i in range(0, len(json_data['queue']), 4)]
            embed_pages = []
            for rp in random_phrases:
                page = discord.Embed(title="Approve Phrases", colour=0xffffff)
                page.add_field(name="Queue", value="".join([f"{p['pos']+1}. {p['text']} | type: {p['type']} | points: "
                                                            f"{p['points']} | author: {p['author']}\n\n" for p in rp]))
                embed_pages.append(page)
            return embed_pages
        embed_pages = gen_menu(json_data)
        index = 0
        menu = await ctx.send(embed=embed_pages[index])
        for emoji in ['✅', '🚫', '❌', '◀️', '▶️']:
            await menu.add_reaction(emoji=emoji)
        while True:
            react = await self.checker(menu, re_check)
            if str(react.emoji) == '🚫' or react is None:
                json.dump(json_data, open(self.client.random_phrases, "w"), indent=4)
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
                        msg = await self.client.wait_for('message', timeout=60, check=msg_check)
                        int(msg.content)
                    except ValueError:
                        await ctx.send("Make sure to choose a number!", delete_after=5)
                        continue
                    if int(msg.content) - 1 in range(len(json_data['queue'])):
                        try:
                            if str(react.emoji) == '✅':
                                json_data['phrases'].append([i for i in json_data['queue'] if i['pos'] == int(msg.content) - 1][0])
                            json_data['queue'].pop(json_data['queue'].index([i for i in json_data['queue'] if i['pos'] == int(msg.content) - 1][0]))
                            embed_pages = gen_menu(json_data)
                        except IndexError:
                            await ctx.send("Make sure to choose a numbered item!", delete_after=5)
                    await msg.delete()
                [await menu.add_reaction(emoji=emoji) for emoji in ['◀️', '▶️']]
                embed_pages[index].title = "Approve Phrases"
                embed_pages[index].colour = 0xFFFFFF
                await menu.edit(embed=embed_pages[index])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if "buh!" in message.content:
            return
        wchk = self.word_check(message.content)
        if wchk[1]:
            await message.delete()
            return
        self.update_phrase(message.content)


def setup(client):
    client.add_cog(PhrasesCog(client))
