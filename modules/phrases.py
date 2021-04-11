import asyncio
import discord
import json
import sentry_sdk
import logging
from fuzzywuzzy import fuzz, process
from discord.ext import commands

sentry_sdk.init(
    json.load(open("conf_files/conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)


class PhrasesCog(commands.Cog, name="phrases"):
    def __init__(self, client):
        self.client = client
        self.client.phr_db_file = "db_files/phrases.json"

    def word_check(self, msg):
        rslur = ["retard", "r*tard", "ret*rd"]
        nslur = ["nigger", "n*gger", "nigga", "n*gga"]
        chks = process.extract(msg.lower(), nslur, scorer=fuzz.token_set_ratio) + process.extract(msg.lower(), rslur,
                                                                                                  scorer=fuzz.token_set_ratio)
        chks.sort(key=lambda x: x[1], reverse=True)
        for w in chks:
            if w[1] > 90:
                return (chks, True)
        return (chks, False)

    async def cog_before_invoke(self, ctx):
        # self.logger.info(f"{ctx.author.name} ran {ctx.command} with message {ctx.message.content}")
        pass

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
        string_to_print = ""
        for phrase in data["phrases"]:
            string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
        await ctx.send(string_to_print)

    @commands.command(aliases=['arp'])
    async def add_rphrase(self, ctx: discord.Message):
        json_data = json.load(open(self.client.random_phrases))
        types = {'1️⃣': "spell", '2️⃣': "steal", '3️⃣': "beg"}
        gl = {'1️⃣': "win", '2️⃣': "lose", ":beg_two:": "big win"}

        async def checker(msg, check_func):
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30, check=check_func)
                await msg.remove_reaction(emoji=reaction, member=user)
                return reaction
            except asyncio.TimeoutError:
                return None

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

        react = await checker(user_msg, type_emb_check)

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
        react2 = await checker(user_msg, gl_emb_check)

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
    async def approve_rphrases(self, ctx):
        json_data = json.load(open(self.client.random_phrases))
        if len(json_data['queue']) == 0:
            return await ctx.send("No messages in queue!", delete_after=7)
        emb = discord.Embed()
        limit = 4
        test = True
        while test:
            emb_text = ""
            for i in json_data['queue'][0:limit]:
                emb_text += str(json_data['queue'].index(i) + 1) + '. ' + str(i['text']) + ' | type: ' + str(
                    i['type']) + ' | points: ' + str(i['points']) + ' | author: ' + str(i['author']) + '\n\n'
            emb.add_field(name="Queue", value=emb_text)
            limit -= 1
            if len(emb) < 6000:
                test = False
        await ctx.send("Reply to the embed with r<#> (remove #) or a<#> (add #).\n(ex. r1 a2 a3 a4 r5)",
                       delete_after=10)
        await ctx.send(embed=emb, delete_after=30)
        try:
            msg = await self.client.wait_for('message', timeout=30.0)
        except asyncio.exceptions.TimeoutError:
            await ctx.send("Operation timed out!", delete_after=5)
            return
        await msg.delete()
        apr = msg.content.split(" ")
        approve = [int(i.strip("a")) - 1 for i in apr if "a" in i]
        remove = [int(i.strip("r")) - 1 for i in apr if "r" in i]
        for i in range(len(apr)):
            for j in json_data['queue']:
                t = json_data['queue'].pop(json_data['queue'].index(j))
                if j['pos'] in approve:
                    del t['pos']
                    json_data['phrases'].append(t)
                elif j['pos'] in remove:
                    pass
                else:
                    json_data['queue'].append(t)
        for j in json_data['queue']:  # reset positions in queue
            j['pos'] = json_data['queue'].index(j)
        json.dump(json_data, open(self.client.random_phrases, 'w'), indent=4)
        await ctx.send("Phrase approval changes done!", delete_after=10)

    @commands.Cog.listener()
    async def on_message(self, message):
        wchk = self.word_check(message.content)
        if message.author == self.client.user:
            return
        if wchk[1]:
            await message.delete()
            await message.author.send(f"Don't use the word \"{wchk[0][0][0]}\"!", delete_after=60)
            return
        self.update_phrase(message.content)


def setup(client):
    client.add_cog(PhrasesCog(client))
