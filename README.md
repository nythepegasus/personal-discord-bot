# Nikki's Personal Discord Bot
This is my own Discord bot that I have created for a personal server. It keeps track of phrases and different house's points. It's not fully complete, but it's pretty far along.
### Information
All data is now stored in a MongoDB database. I use `mongoengine` to access MongoDB, and you can see all the code connecting the bot to MongoDB in `utils/schema.py`.

More information can be found in the wiki (TODO) about specific things.
### Installation
Clone the repository into the directory you want to store the bot using:

`git clone https://github.com/nythepegasus/personal-discord-bot.git`

Then run:

`python3 -m pip install -r requirements.txt`

You then have to go through the config file and fill out all the desired options you will need. MongoDB is required for the bot to run, so make sure you have it running somewhere you can connect to it.

Once everything is in `conf_files/conf.json` You can then run `python3 main.py` to get the bot up and running. 
