import json
import random
import discord
import asyncio
import typing
from pathlib import Path
from discord.ext import commands


class GamesCog(commands.Cog, name="games"):
    def __init__(self, client):
        self.client = client
        self.players_dir = Path("db_files/players/")
        self.trivia_questions = Path("db_files/trivia.json")

    async def checker(self, msg: discord.Message, check_func, timeout: int = 30) -> typing.Union[
        discord.Reaction, None]:
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=timeout, check=check_func)
            await msg.remove_reaction(emoji=reaction, member=user)
            return reaction
        except asyncio.TimeoutError:
            await msg.delete()
            return None

    @commands.command(name="trivia")
    async def trivia(self, ctx):
        plyr_data = json.load((self.players_dir / f"{ctx.author.id}.json").open())
        questions = json.load(self.trivia_questions.open())

        def re_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

        mp = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3}
        question_to_ask = random.choice(questions['not_asked'])
        questions['not_asked'].pop(questions['not_asked'].index(question_to_ask))
        questions['asked'].append(question_to_ask)

        triv_emb = discord.Embed(title="Trivia!", colour=random.randint(0, 0xFFFFFF))
        triv_emb.add_field(name=question_to_ask['question'], value="\n\n".join(
            [f"{question_to_ask['answers'].index(i) + 1}. {i}" for i in question_to_ask['answers']]))
        triv_msg = await ctx.send(embed=triv_emb)
        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
            await triv_msg.add_reaction(emoji=emoji)

        react = await self.checker(triv_msg, re_check, timeout=90)
        chg = "right" if mp[str(react.emoji)] == question_to_ask['right_answer'] else "wrong"
        pts = 100 if chg == "right" else -15

        await ctx.author.send(f"You got it {chg}!\nYou earned {pts} points.", delete_after=10)

        plyr_data['points_earned'].append(pts)
        question_to_ask['times_correct' if chg == "right" else 'times_wrong'] += 1

        json.dump(questions, self.trivia_questions.open('w'), indent=4)
        json.dump(plyr_data, (self.players_dir / f'{ctx.author.id}.json').open('w'), indent=4)

        await triv_msg.delete()

    @commands.command(name="add_trivia")
    async def add_trivia(self, ctx):
        mp = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3}
        questions = json.load(self.trivia_questions.open())

        def msg_check(msg: discord.Message):
            return msg.author == ctx.author

        def re_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

        question_embed = discord.Embed(title="Adding Trivia Question!",
                                       description="Type your trivia question to the bot!")
        question_msg = await ctx.send(embed=question_embed)

        try:
            msg = await self.client.wait_for('message', timeout=60, check=msg_check)
            question = msg.content
        except asyncio.TimeoutError:
            await question_msg.delete()
            return await ctx.send("Question input timed out.", delete_after=7)

        await question_msg.delete()
        await msg.delete()

        answer_embed = discord.Embed(title="Adding Question Answers",
                                     description="Add the answers to the question separated with new lines.")
        answer_msg = await ctx.send(embed=answer_embed)

        try:
            msg = await self.client.wait_for('message', timeout=60, check=msg_check)
            answers = msg.content
        except asyncio.TimeoutError:
            await answer_msg.delete()
            return await ctx.send("Question input timed out.", delete_after=7)

        await answer_msg.delete()
        await msg.delete()

        if len(msg.content.split("\n")) != 4:
            await ctx.author.send(f"Your question: {question}\nYour answers: {answers}\n\n"
                                  f"(You can react with a 🗑 to delete this message at any time.)")
            return await ctx.send("Your question must have 4 answers!")
        else:
            answers = answers.split("\n")

        which_emb = discord.Embed(title="Which One Is Correct?",
                                  description="React which one of your answers is correct.")
        which_msg = await ctx.send(embed=which_emb)
        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
            await which_msg.add_reaction(emoji=emoji)

        react = await self.checker(which_msg, re_check)

        await which_msg.delete()

        question_to_add = {
            "question": question,
            "right_answer": mp[str(react.emoji)],
            "times_correct": 0,
            "times_wrong": 0,
            "answers": answers
        }

        questions['queue'].append(question_to_add)
        json.dump(questions, self.trivia_questions.open("w"), indent=4)

        await ctx.send("Your question has been added to the queue!\n"
                       "Hopefully you don't see it soon, and someone else gets to answer it!", delete_after=7)


def setup(client):
    client.add_cog(GamesCog(client))
