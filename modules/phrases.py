import discord
import json
import sentry_sdk
from discord.ext import commands

sentry_sdk.init(
    json.load(open("conf.json", "r"))["sentry_sdk"],
    traces_sample_rate=1.0
)


class PhrasesCog(commands.Cog, name="Phrases Commands"):
    def __init__(self, client):
        self.client = client
        self.db_file = "db_files/phrases.json"
        self.tonys_a_cunt = [
            "\u0628",
            "\u064d",
            "\u0631",
            "nigger",
            "nigga"
        ]

    @commands.command(name="add_phrase", aliases=["ap"])
    async def add_phrase(self, ctx, phrase):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        data = json.load(open(self.db_file))
        try:
            cur_index = data["phrases"][-1]["uid"] + 1
        except IndexError:
            cur_index = 1
        for line in data["phrases"]:
            if phrase == line["phrase"]:
                msg = await ctx.send("Phrase already exists!")
                await msg.delete(delay=5)
                return
            elif len(phrase) <= 2:
                msg = await ctx.send("Phrase too short!")
                await msg.delete(delay=5)
                return
            elif len(phrase) >= 35:
                msg = await ctx.send("Phrase too long!")
                await msg.delete(delay=5)
                return
            elif any(bad in phrase.lower() for bad in self.tonys_a_cunt):
                msg = await ctx.send("You're a cunt!")
                await msg.delete(delay=5)
                return
        add_phrase = {
            "uid": cur_index,
            "phrase": phrase,
            "times_said": 0,
        }
        with open(self.db_file, "w") as f:
            data["phrases"].append(add_phrase)
            f.write(json.dumps(data, indent=4))
            msg = await ctx.send("Phrase added!")
            await msg.delete(delay=5)

    def update_phrase(self, phrase):
        data = json.load(open(self.db_file))
        for d in data["phrases"]:
            if d.get("phrase").lower() in phrase.lower():
                d["times_said"] += 1
        with open(self.db_file, "w") as f:
            f.write(json.dumps(data, indent=4))
            return "Updated phrase!"

    @commands.command(name="remove_phrase", aliases=["rp"])
    async def remove_phrase(self, ctx, phrase):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()

        data = json.load(open(self.db_file))
        with open(self.db_file, "w") as f:
            data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
            f.write(json.dumps(data, indent=4))
            msg = await ctx.send("Removed phrase!")
            await msg.delete(delay=5)

    @commands.command(name="phrase_counts", aliases=["pc"])
    async def phrase_counts(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel) and not isinstance(ctx.channel, discord.channel.GroupChannel):
            await ctx.message.delete()
        data = json.load(open(self.db_file))
        string_to_print = ""
        for phrase in data["phrases"]:
            string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
        await ctx.send(string_to_print)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if any(bad in message.content.lower() for bad in self.tonys_a_cunt):
            await message.delete()
            return
        self.update_phrase(message.content)



def setup(client):
    client.add_cog(PhrasesCog(client))
