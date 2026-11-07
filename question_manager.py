import json

from config import QUESTIONS_FILE


def save_questions(questions):

    data = {
        "questions": questions
    }

    with open(QUESTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_questions():

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["questions"]


def get_question_for_stage(questions, stage):

    index = stage - 1

    if 0 <= index < len(questions):
        return questions[index]

    return None