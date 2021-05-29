import json
import mongoengine
import pathlib
from schema import *

conf_data = json.load(open("conf_files/conf.json"))
mongoconf = conf_data['mongodb']
mongoengine.connect(host=f"mongodb://{mongoconf['user']}:{mongoconf['password']}@"
                         f"{mongoconf['ipport']}/{mongoconf['db']}?authSource=admin")
print("Connected to MongoDB!")

rand_phrases = json.load(open("db_files/random_texts.json"))['phrases']

print(f"Converting {len(rand_phrases)} random phrases..")

for rphrase in rand_phrases:
    RandomText(type=rphrase['type'], points=rphrase['points'], text=rphrase['text'], author=rphrase['author'],
               queue = False).save()

print(f"Converting done!")

phrases = json.load(open("db_files/phrases.json"))['phrases']

print(f"Adding {len(phrases)} phrases to the tracker under dummy player..")

dummy = Player(dis_id="dummy", name="dummy", house="Slytherin", items=[]).save()

for phrase in phrases:
    p = Phrase(phrase=phrase['phrase'], adder="The OG Gang").save()
    PhraseCount(phrase=p, said=dummy, times=phrase['times_said']).save()

players = list(pathlib.Path("db_files/players/").glob("**/*"))

for player in players:
    pdata = json.load(player.open())
    p = Player(dis_id=player.stem, name=pdata['name'], house=pdata['house'], items=pdata['items']).save()
    for points in pdata['points_earned']:
        Points(player=p, house=p.house, type="transfer", points=points, season=2).save()
    for points in pdata['season_history'][0]:
        Points(player=p, house=p.house, type="transfer", points=points, season=1).save()
