import os
import discord
import csv

csv.register_dialect('mydialect', delimiter="|")

words_to_track_file = "phrases.csv"

fields = ['phrase', 'times_said']

def add_phrase(phrase):
    with open(words_to_track_file, "r") as f:
        csvreader = csv.DictReader(f, fieldnames=fields, dialect='mydialect')
        for row in csvreader:
            if phrase in list(row.values())[0]:
                return "Phrase already exists!"
            elif "|" in phrase:
                return "Invalid character in phrase!"
            elif len(phrase) >= 35:
                return "Phrase too long!"
    with open(words_to_track_file, "a") as f:
        csvwriter = csv.DictWriter(f, fieldnames=fields, dialect='mydialect')
        csvwriter.writerow({'phrase': phrase, 'times_said': 0})
        return "Phrase added!"

def update_phrase(phrase):
    file = open(words_to_track_file).readlines()
    phrase_list = []
    for item in file:
        if item.split("|")[0].lower() in phrase.lower():
            phrase_list.append(item.replace(item.split("|")[-1], str(int(item.split("|")[-1]) + 1) + "\n"))
        else:
            phrase_list.append(item)
    with open(words_to_track_file, "w") as f:
        f.writelines(phrase_list)
    return "Updated phrase!"


TOKEN = "NTIxNTUwNzIyMzU0MTE4NjY2.XqzV7Q.gvob9l9tcZe2_W_vH_54Y-shW1A"
client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"Tester in {guild}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "buh!help" in message.content:
        await message.channel.send("buh!add_phrase\t\tAdds phrase to count\nbuh!phrases_counts\t\tShows current phrases counts.")
        return
    elif "buh!add_phrase" in message.content:
        await message.channel.send(add_phrase(message.content.replace("buh!add_phrase ", "")))
        return
    elif "buh!phrases_counts" == message.content:
        phrases = open(words_to_track_file).readlines()
        string_to_print = ""
        for phrase in phrases:
            string_to_print += f"{phrase.split('|')[0]}: {phrase.split('|')[1]}"
        await message.channel.send(string_to_print)
        return
    update_phrase(message.content)


client.run(TOKEN)
