import json

def load_questions():

    with open("questions.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["questions"]

questions = load_questions()

print(questions[0]["question"])
print(questions[0]["options"]["A"])

# 1. User uploads study notes
user_information = load_text_file()

# 2. Generate 10 questions
generate_questions(user_information, num_questions=10)

# 3. Questions are saved in questions.json

# 1. Load saved questions
questions = load_questions()

# 2. Retrieve question for current stage
question_data = get_question_for_stage(
    questions,
    current_stage
)

# 3. Display question in Pygame