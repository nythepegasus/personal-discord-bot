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
        chks.sort(reverse=True)
        for w in chks:
            if w[1] > 90:
                return (chks, True)
        return (chks, False)

    async def cog_before_invoke(self, ctx):
        self.logger.info(f"{ctx.author.name} ran {ctx.command} with message {ctx.message.content}")

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
    async def add_rphrase(self, ctx, *, phrase):
        json_data = json.load(open(self.client.random_phrases))
        args = phrase.split(" | ")
        if args[0] not in ["spell", "steal", "beg"]:
            return await ctx.send("Incorrect type specified!\nType must be `spell` or `steal` or `beg`!",
                                  delete_after=7)
        if args[0] == "beg" and args[1] not in ["win", "big"]:
            return await ctx.send("Incorrect win type specified for beg command!\nMust be `win` or `big win`!",
                                  delete_after=7)
        if args[0] in ["spell", "steal"] and args[1] not in ["win", "lose"]:
            return await ctx.send("Incorrect win type specified!\nMust be `win` or `lose`!", delete_after=7)
        if len(args) not in [3, 4]:
            return await ctx.send("Incorrect input! Please retype your phrase in the correct format.\n"
                                  "`buh!add_phrase type | winlose | text with {house} and {points}` | author (optional)",
                                  delete_after=15)
        if "{house}" not in args[2] and "{points}" not in args[2]:
            return await ctx.send("Phrase doesn't contain proper {house} and {points}! Retype it with proper braces!",
                                  delete_after=10)
        phrase_to_add = {
            'type': args[0],
            'points': args[1],
            'text': args[2],
            'author': args[3] if len(args) == 4 else ctx.author.nick or ctx.author.name,
            'pos': len(json_data['queue'])
        }
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
