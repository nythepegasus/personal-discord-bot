# Nikki's Personal Discord Bot
This is my own Discord bot that I have created for a personal server. It keeps track of phrases and different house's points. It's not fully complete, but it's pretty far along.
### Information
All data that this bot uses is held within the `db_files` directory within their own `json` files.
* `phrases.json` holds how many times a specific phrase/word has been said within the server.
* `points.json` holds the information for each player, it has their season histories, point history for the current season, and much more.
* `random_phrases.json` holds all the random phrases used by the different point commands. 
* `amongus.json` holds information for the (albeit scuffed) Among Us cog.

More information can be found in the wiki (TODO) about specific things.
### Installation
Clone the repository into the directory you want to store the bot using:

`git clone https://github.com/nythepegasus/personal-discord-bot.git`

Then run:

`python3 -m pip install -r requirements.txt`

Run `python3 main.py` and it'll go through a first run time asking for `TOKEN`, `owner_id`, and `command_prefix`.

You can also edit the config yourself in `conf_files/conf.json`.
