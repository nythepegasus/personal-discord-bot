import asyncio
import json
import random
import typing
import discord
from discord.ext import commands

from utils.schema import TriviaQuestion, TriviaAnswer, Player, Points


class GamesCog(commands.Cog, name="Games"):
    def __init__(self, client):
        self.client = client
        self.description = "This module adds various games that can be played."
        self.season = json.load(open("db_files/points.json"))['cur_season']

    async def checker(self, msg: discord.Message, check_func, timeout: int = 30) -> \
            typing.Union[discord.Reaction, None]:
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=timeout, check=check_func)
            return reaction
        except asyncio.TimeoutError:
            await msg.delete()
            return None

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(name="trivia")
    async def trivia(self, ctx):
        if not TriviaQuestion.objects:
            return await ctx.send("No trivia questions to be asked!\nYou can help by adding some though.", delete_after=7)

        if not TriviaQuestion.objects(asked=False):
            for question in TriviaQuestion.objects(asked=True):
                question.update(asked=False)

        player = Player.objects(dis_id=str(ctx.author.id)).first()

        def re_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

        mp = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3}
        question_to_ask = random.choice(TriviaQuestion.objects(asked=False))
        question_to_ask.update(asked=True)

        triv_emb = discord.Embed(title="Trivia!", colour=random.randint(0, 0xFFFFFF))
        triv_emb.add_field(name=question_to_ask.question, value="\n\n".join(
            [f"{question_to_ask.answers.index(i) + 1}. {i}" for i in question_to_ask.answers]))
        triv_msg = await ctx.author.send(embed=triv_emb)
        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
            await triv_msg.add_reaction(emoji=emoji)

        react = await self.checker(triv_msg, re_check, timeout=90)
        chg = "right" if mp[str(react.emoji)] == question_to_ask.right_answer else "wrong"
        pts = 100 if chg == "right" else -15

        await ctx.author.send(f"You got it {chg}!\nYou earned {pts} points.", delete_after=10)

        Points(player=player, house=player.house, type="trivia", points=pts, season=self.season).save()
        TriviaAnswer.objects(question=question_to_ask).upsert_one(set__player=player, inc__correct=1 if pts > 0 else 0,
                                                                  inc__wrong=1 if pts < 0 else 0)

        await triv_msg.delete()

    @trivia.error
    async def trivia_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Wait {round(error.retry_after, 2)} more seconds.", delete_after=7)
        else:
            raise error

    @commands.command(name="add_trivia")
    async def add_trivia(self, ctx):
        mp = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3}

        def msg_check(msg: discord.Message):
            return msg.author == ctx.author

        def re_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

        question_embed = discord.Embed(title="Adding Trivia Question!",
                                       description="Type your trivia question to the bot!")
        question_msg = await ctx.author.send(embed=question_embed)

        try:
            msg = await self.client.wait_for('message', timeout=90, check=msg_check)
            question = msg.content
        except asyncio.TimeoutError:
            await question_msg.delete()
            return await ctx.send("Question input timed out.", delete_after=7)

        await question_msg.delete()

        answer_embed = discord.Embed(title="Adding Question Answers",
                                     description="Add the answers to the question separated with new lines.")
        answer_msg = await ctx.author.send(embed=answer_embed)

        try:
            msg = await self.client.wait_for('message', timeout=120, check=msg_check)
            answers = msg.content
        except asyncio.TimeoutError:
            await answer_msg.delete()
            return await ctx.send("Question input timed out.", delete_after=7)

        await answer_msg.delete()

        if len(msg.content.split("\n")) != 4:
            await ctx.author.send(f"Your question: {question}\nYour answers: {answers}\n\n"
                                  f"(You can react with a️ 🗑️ to delete this message at any time.)")
            return await ctx.author.send("Your question must have 4 answers!", delete_after=7)
        else:
            answers = answers.split("\n")

        which_emb = discord.Embed(title="Which One Is Correct?",
                                  description="React which one of your answers is correct.")
        which_msg = await ctx.author.send(embed=which_emb)
        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
            await which_msg.add_reaction(emoji=emoji)

        right_react = await self.checker(which_msg, re_check)

        await which_msg.delete()

        author_check = await ctx.author.send(
            embed=discord.Embed(title="Do you want to add an author?", description="React with yes or no to choose."))

        [await author_check.add_reaction(emoji=emoji) for emoji in ["✅", "❌"]]

        author_react = await self.checker(author_check,
                                          lambda reaction, user: user == ctx.author and str(reaction.emoji) in ["✅",
                                                                                                                "❌"])

        if author_react is None or str(author_react.emoji) == "❌":
            author = ""
        else:
            try:
                await ctx.author.send("```Please input author name```")
                author_msg = await self.client.wait_for('message', timeout=60, check=msg_check)
                author = author_msg.content
            except asyncio.TimeoutError:
                await ctx.send("Author input timed out.\nUsing blank author instead.", delete_after=7)
                author = ""

        await author_check.delete()
        TriviaQuestion(question=question, right_answer=mp[str(right_react.emoji)], asked=False, answers=answers,
                       author=author, queue=True).save()

        await ctx.author.send("Your question has been added to the queue!\n"
                              "Hopefully you don't see it soon, and someone else gets to answer it!", delete_after=7)
    


def setup(client):
    client.add_cog(GamesCog(client))
