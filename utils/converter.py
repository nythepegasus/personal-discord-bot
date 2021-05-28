import json
import mongoengine
import pathlib
from schema import *

mongoengine.disconnect()
mongoengine.connect(db="discord_bot_testing",
                    host="mongodb://admin:Job-Wildlife-Claw-Reflector6-Decibel@192.168.1.30:27017/?authSource=admin")

# print(len(json.load(open("db_files/random_texts.json"))['phrases']))

# for rphrase in rand_phrases['phrases']:
#     RandomText(type=rphrase['type'], points=rphrase['points'], text=rphrase['text'], author=rphrase['author'], queue=False).save()

phrases = json.load(open("db_files/phrases.json"))

dummy = Player(dis_id="dummy", name="dummy", house="Slytherin", items=[]).save()

for phrase in phrases['phrases']:
    p = Phrase(phrase=phrase['phrase'], adder="The OG Gang").save()
    PhraseCount(phrase=p, said=dummy, times=phrase['times_said']).save()

# players = list(pathlib.Path("db_files/players/").glob("**/*"))
#
# for player in players:
#     pdata = json.load(player.open())
#     p = Player(dis_id=player.stem, name=pdata['name'], house=pdata['house'], items=pdata['items']).save()
#     for points in pdata['points_earned']:
#         Points(player=p, house=p.house, type="transfer", points=points, season=2).save()
#     for points in pdata['season_history'][0]:
#         Points(player=p, house=p.house, type="transfer", points=points, season=1).save()
