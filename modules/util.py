import psutil, subprocess, time, datetime, speedtest, discord, gspread, json, logging
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials


class UtilCog(commands.Cog, name="Utility Commands"):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=["h"])
    async def help(self, ctx):
        help_emb = discord.Embed(title="Bot Commands", colour=0x00adff)
        help_emb.add_field(name="buh!add_phrase | buh!ap", value="Add phrase to the tracker", inline=False)
        help_emb.add_field(name="buh!remove_phrase | buh!rp", value="Remove phrase from the tracker", inline=False)
        help_emb.add_field(name="buh!phrases_counts | buh!pc", value="Check phrases on the tracker", inline=False)
        help_emb.add_field(name="buh!archive_pins | buh!arcp", value="Archive all pins from #general chat", inline=False)
        help_emb.add_field(name="buh!house_points | buh!hp", value="Check each house's points.", inline=False)
        help_emb.add_field(name="buh!cast_spell | buh!cs", value="Gamble your house's points away, and see where fate takes you.", inline=False)
        help_emb.add_field(name="buh!stats", value="Check the discord bot's current server stats", inline=False)
        help_emb.add_field(name="buh!netstats", value="Check the discord bot's current net stats", inline=False)
        help_emb.add_field(name="More to come!", value=":3", inline=False)
        help_emb.set_footer(text="Developed by Nikki")
        await ctx.send(embed=help_emb)


    @commands.command(name="archive_pins", aliases=["arcp"])
    async def archive_pins(self, ctx):
        guild = self.client.guilds[0]
        for channel in guild.channels:
            if channel.name == "general":
                general_chat = channel
        for channel in guild.channels:
            if channel.name == "archived-pins":
                archive_channel = channel
        myPins = await general_chat.pins()
        if len(myPins) == 0:
            await ctx.send("No more pins")
        for pin in myPins:
            emb = discord.Embed(
                description = pin.content,
                timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
            )
            emb.set_author(
                name=pin.author,
                icon_url=pin.author.avatar_url,
                url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                    pin.guild.id, pin.channel.id, pin.id)
            )
            if pin.attachments:
                if len(pin.attachments) > 1:
                    img_url = pin.attachments[0].url
                    emb.set_image(url=img_url)
                    emb.set_footer(text=f"Part 1 | Archived from #{pin.channel}")
                    await archive_channel.send(embed=emb)
                    attach_counter = 1
                    try:
                        for attachment in pin.attachments:
                            next_emb = discord.Embed(
                                timestamp = datetime.datetime.utcfromtimestamp(int(time.time())),
                            )
                            next_emb.set_author(
                            name=pin.author,
                            icon_url=pin.author.avatar_url,
                            url="https://discordapp.com/channels/{0}/{1}/{2}".format(
                                pin.guild.id, pin.channel.id, pin.id)
                            )
                            img_url = pin.attachments[attach_counter].url
                            next_emb.set_image(url=img_url)
                            next_emb.set_footer(text=f"Part {attach_counter+1} | Archived from #{pin.channel}")
                            attach_counter += 1
                            await archive_channel.send(embed=next_emb)
                    except IndexError:
                        pass
                elif len(pin.attachments) == 1:
                    img_url = pin.attachments[0].url
                    emb.set_image(url=img_url)
                    emb.set_footer(text=f"Archived from #{pin.channel}")
                    await archive_channel.send(embed=emb)
            else:
                await archive_channel.send(embed=emb)
            await pin.unpin()
        await ctx.send(f"Archived the pins! Check them out in #{archive_channel}!")


    @commands.command()
    async def stats(self, ctx):
        uptime = subprocess.run("uptime", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        days = int(uptime.stdout.split()[2])
        hours = str(int(uptime.stdout.split()[4].strip(b",").split(b":")[0])).zfill(2)
        minutes = str(int(uptime.stdout.split()[4].strip(b",").split(b":")[1])).zfill(2)
        stat_emb = discord.Embed(title="Discord Bot's Server Stats", colour=0x00adff)
        stat_emb.add_field(name="Current Uptime", value=f"{days}:{hours}:{minutes}")
        stat_emb.add_field(name="RAM Percentage", value=psutil.virtual_memory()[2])
        stat_emb.add_field(name="CPU Percentage", value=psutil.cpu_percent())
        stat_emb.set_footer(text="Proudly fixed with nano.")
        await ctx.send(embed=stat_emb)


    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.command()
    async def netstats(self, ctx):
        async with ctx.typing():
            s = speedtest.Speedtest()
            s.get_best_server()
            s.download(threads=4)
            s.upload(threads=4)
            url = s.results.share()
            net_emb = discord.Embed(title="Discord Bot's Network Speeds", colour=0x00adff)
            net_emb.set_image(url=url)
            await ctx.send(embed=net_emb)

    @netstats.error
    async def netstats_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Wait {round(error.retry_after, 2)} more seconds.")
        else:
            raise error

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(aliases=["urp"])
    async def update_random_phrases(self, ctx):
        logging.basicConfig(filename='logs/gsheets.log', level=logging.DEBUG)
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Discord Bot Stuffs").sheet1
        data = sheet.get_all_values()
        data.pop(0)
        for row in data:
            json_data = json.load(open("random_texts.json"))
            row.pop(0)  # Clean by getting rid of the timestamp
            while("" in row):
                row.remove("")  # Get rid of all empty things, which cleans up selecting things too
            if len(row) == 0 or row[0] == "" or len(row) == 2:
                continue
            if len(row) == 4:
                author = row[3]
            else:
                author = ""
            if row[2] in json_data["all_phrases"]:
                continue
            if row[1] == "Gain" or row[1] == "Big Gain":
                try:
                    row[2].format(house="Test", points="Test")
                except KeyError:
                    logging.warning("This didn't have the proper keys:\nPhrase: {}\nBy: {}".format(row[2], author))
                    continue
                if row[1] == "Big Gain":
                    json_data["beg_texts"]["big_gain_texts"].append({"big_gain_text": row[2], "author": author})
                elif row[0] == "Spell text.":
                    json_data["spell_texts"]["gain_texts"].append({"gain_text": row[2], "author": author})
                elif row[0] == "Steal text.":
                    json_data["steal_texts"]["gain_texts"].append({"gain_text": row[2], "author": author})
                elif row[0] == "Beg text.":
                    json_data["beg_texts"]["gain_texts"].append({"gain_text": row[2], "author": author})
            elif row[1] == "Lose":
                try:
                    row[2].format(house="Test", points="Test")
                except KeyError:
                    logging.warning("This didn't have the proper keys:\nPhrase: {}\nBy: {}".format(row[2], author))
                    continue
                if row[0] == "Spell text.":
                    json_data["spell_texts"]["lose_texts"].append({"lose_text": row[2], "author": author})
                elif row[0] == "Steal text.":
                    json_data["steal_texts"]["lose_texts"].append({"lose_text": row[2], "author": author})

            json_data["all_phrases"].append(row[2])
            json.dump(json_data, open("random_texts.json", "w"), indent=4)
        await ctx.send("Phrases updated! Hopefully you see yours soon ;)")


def setup(client):
    client.add_cog(UtilCog(client))
