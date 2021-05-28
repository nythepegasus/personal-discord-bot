from mongoengine import StringField, ReferenceField, ListField, DictField, IntField, DateTimeField, BooleanField
from mongoengine import Document


class Player(Document):
    dis_id = StringField(unique=True, required=True)
    name = StringField(required=True)
    house = StringField(required=True)
    items = ListField()
    emb_conf = DictField(required=True, default={"color": "0x00adff", "shown": ["timeouts", "items", "phrases", "command_usages"]})
    rng_stats = DictField(required=True, default={"cast": 0, "beg": 0, "steal": 0})
    meta = {"collection": "players"}


class Points(Document):
    player = ReferenceField(Player, required=True)
    house = StringField(required=True)
    type = StringField(required=True)
    points = IntField(required=True)
    season = IntField(required=True)
    meta = {"collection": "points"}


class Item(Document):
    name = StringField(required=True)
    attrs = DictField(required=True)
    price = IntField(required=True)
    meta = {"collection": "items"}


class RandomText(Document):
    type = StringField(required=True)
    points = StringField(required=True)
    text = StringField(required=True)
    author = StringField()
    queue = BooleanField(required=True)
    meta = {"collection": "random_texts"}


class Phrase(Document):
    phrase = StringField(required=True)
    adder = StringField(required=True)
    meta = {"collection": "phrases"}


class PhraseCount(Document):
    phrase = ReferenceField(Phrase, required=True)
    said = ReferenceField(Player, required=True)
    times = IntField()
    meta = {"collection": "phrase_counts"}


class CommandUsage(Document):
    command = StringField(required=True)
    said = ReferenceField(Player, required=True)
    times = IntField()
    meta = {"collection": "command_uses"}


class Timeout(Document):
    player = ReferenceField(Player, required=True)
    reason = StringField(required=True)
    until = DateTimeField(required=True)
    meta = {"collection": "timeouts"}


class TriviaQuestion(Document):
    question = StringField(required=True)
    right_answer = IntField(required=True)
    asked = BooleanField()
    answers = ListField(required=True)
    author = StringField()
    queue = BooleanField(required=True)
    meta = {"collection": "trivia_questions"}


class TriviaAnswer(Document):
    question = ReferenceField(TriviaQuestion)
    player = ReferenceField(Player)
    correct = IntField()
    wrong = IntField()
    meta = {"collection": "trivia_responses"}

if __name__ == "__main__":
    import mongoengine
    import json
    conf_data = json.load(open("conf_files/conf.json"))
    mongoconf = conf_data['mongodb']
    mongoengine.connect(host=f"mongodb://{mongoconf['user']}:{mongoconf['password']}@"
                             f"{mongoconf['ipport']}/{mongoconf['db']}?authSource=admin", )
    print("Connected to MongoDB!")
