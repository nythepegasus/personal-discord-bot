import random, json


def ask_trivia_question():
    data = json.load(open("trivia.json"))
    if len(data["trivia_questions_not_asked"]) == 0:
        print("Oopsie poopsie, no more trivia questions.\nResetting questions..")
        reset_trivia_questions()
        return

    trivia_question = data["trivia_questions_not_asked"][random.randint(0, (len(data["trivia_questions_not_asked"]) - 1))]

    answers_copy = trivia_question["answers"].copy()

    answers_string = ""

    print(trivia_question["question"])
    for i in range(0, len(trivia_question["answers"])):
        answers_string += f"{str(i+1)}. {answers_copy.pop(random.randint(0, (len(answers_copy)-1)))}"
        answers_string += "\n"
    print(answers_string)

    response = input("Your answer: ")

    if response == trivia_question["answers"][trivia_question["right_answer"]]:
        trivia_question["times_correct"] += 1
        print("Correct!")
    else:
        trivia_question["times_wrong"] += 1
        print("You suck.")

    data["trivia_questions_not_asked"].pop(data["trivia_questions_not_asked"].index(trivia_question))
    data["trivia_questions_asked"].append(trivia_question)

    with open("trivia.json", "w") as f:
        f.write(json.dumps(data, indent=4))

def add_trivia_question(question, answers, right_answer):
    data = json.load(open("trivia.json"))
    trivia_question = {
        "question": question,
        "right_answer": right_answer,
        "times_correct": 0,
        "times_wrong": 0,
        "answers": answers
    }
    data["trivia_questions_not_asked"].append(trivia_question)
    with open("trivia.json", "w") as f:
        f.write(json.dumps(data, indent=4))
    print("Question added!")


def reset_trivia_questions():
    data = json.load(open("trivia.json"))
    for i in data["trivia_questions_asked"]:
        data["trivia_questions_not_asked"].append(i)
    data["trivia_questions_asked"] = []
    json.dump(data, open("trivia.json", "w"), indent=4)
