import json

def load_questions():

    with open("questions.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["questions"]

questions = load_questions()

print(questions[0]["question"])
print(questions[0]["options"]["A"])