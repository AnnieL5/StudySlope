

import pygame

pygame.init()

# Load questions when game starts
questions = load_questions()

current_stage = 1

# Retrieve question for current stage
question_data = get_question_for_stage(
    questions,
    current_stage
)

# Example: player reaches a checkpoint
if question_data:

    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["correct_answer"]

    # Display question
    print(question)

    # Display four options
    for letter, option in options.items():
        print(f"{letter}. {option}")

    # When player selects an option:
    player_answer = "A"

    if player_answer == correct_answer:
        print("Correct! Continue to next stage.")
        current_stage += 1

    else:
        print("Incorrect! Try again.")