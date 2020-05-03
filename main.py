import os
import discord
import json
# from phrases_module import add_phrase, update_phrase, remove_phrase

words_to_track_file = "phrases.json"

tonys_a_cunt = [
        "\u0628",
        "\u064d",
        "\u0631",
]

def add_phrase(phrase):
    data = json.load(open(words_to_track_file))
    try:
        cur_index = data["phrases"][-1]["uid"] + 1
    except IndexError:
        cur_index = 1
    for line in data["phrases"]:
        if phrase == line["phrase"]:
            return "Phrase already exists!"
        elif len(phrase) <= 3:
            return "Phrase too short!"
        elif len(phrase) >= 35:
            return "Phrase too long!"
        elif any(bad in phrase for bad in tonys_a_cunt):
            return "You're a cunt!"
    add_phrase = {
        "uid": cur_index,
        "phrase": phrase,
        "times_said": 0,
    }
    with open(words_to_track_file, "w") as f:
        data["phrases"].append(add_phrase)
        f.write(json.dumps(data, indent=4))
        return "Phrase added!"

def update_phrase(phrase):
    data = json.load(open(words_to_track_file))
    for d in data["phrases"]:
        if d.get("phrase").lower() in phrase.lower():
            d["times_said"] += 1
    with open(words_to_track_file, "w") as f:
        f.write(json.dumps(data, indent=4))
        return "Updated phrase!"

def remove_phrase(phrase):
    data = json.load(open(words_to_track_file))
    with open(words_to_track_file, "w") as f:
        data["phrases"] = [d for d in data["phrases"] if d.get("phrase") != phrase]
        f.write(json.dumps(data, indent=4))
        return "Removed phrase!"


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
    if any(bad in message.content for bad in tonys_a_cunt):
        await message.delete()
        await client.send_message(message.author, "You're a cunt for trying that.")
    mapping = [("buh!help ", ""), ("buh!add_phrase ", ""), ("buh!ap ", ""), ("buh!phrases_counts ", ""), ("buh!pc ", ""), ("buh!remove_phrase ", ""), ("buh!rp ", "")]
    if "buh!help" in message.content:
        await message.channel.send("buh!add_phrase\t\tAdds phrase to count\nbuh!phrases_counts\t\tShows current phrases counts.")
        return
    elif any(com in message.content for com in ["buh!add_phrase", "buh!ap"]):
        for k, v in mapping:
            message.content = message.content.replace(k, v)
        await message.channel.send(add_phrase(message.content))
        return
    elif any(com in message.content for com in ["buh!remove_phrase", "buh!rp"]):
        for k, v in mapping:
            message.content = message.content.replace(k, v)
        await message.channel.send(remove_phrase(message.content))
    elif any(com == message.content for com in ["buh!phrases_counts", "buh!pc"]):
        data = json.load(open(words_to_track_file))
        string_to_print = ""
        for phrase in data["phrases"]:
            string_to_print += f"{phrase['phrase']}: {phrase['times_said']}\n"
        await message.channel.send(string_to_print)
        return
    update_phrase(message.content)


client.run(TOKEN)
