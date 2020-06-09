# Nikki's Personal Discord Bot
This is my own Discord bot that I have created for a personal server. It keeps track of phrases and different house's points. It's not fully complete, but it's pretty far along.
### Information
This bot tracks set phrases, and counts how many times it's said in the server.
That information is kept in `db_files/phrases.json`
___
This bot also has points for the four Hogwarts houses (you could probably change these names if you want)
The points and point related information is kept in `db_files/points.json`

It contains timeouts for the beg command is held, and the last pin count (each pin awarding the pin-ee's house 50 points.)
___
The different point commands have random outputs, and the random outputs are kept in `db_files/random_texts.json`

These can be updated through a Google Forms and Google Sheets using `oauth2client` and `gspread` (TODO: Find a way to share the Google Form layout)
___
### Installation
Clone the repository into the directory you want to store the bot using:

`git clone https://github.com/nythepegasus/personal-discord-bot.git`

Run `python3 main.py` and it'll go through a first run time asking for `TOKEN`, `owner_id`, and `command_prefix`.

You can also edit the config yourself in `conf_files/conf.json`.
