import os
import json
from openai import OpenAI

from groq import Groq
from dotenv import load_dotenv

from config import NUM_QUESTIONS, OPTIONS
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)



# api_key = os.getenv("GROQ_API_KEY")

# if not api_key:
#     raise ValueError("GROQ_API_KEY is missing from your .env file.")


def generate_questions(user_information, num_questions=NUM_QUESTIONS):

    prompt = f"""
    Based on the following study notes, generate exactly {num_questions}
    multiple-choice questions.

    Requirements:
    - Each question must have exactly four options.
    - There must be exactly one correct answer.
    - Questions should test understanding of the study material.
    - Do not create questions about information absent from the notes.

    Study notes:
    {user_information}

    Return valid JSON in this exact format:

    {{
        "questions": [
            {{
                "question": "What is ...?",
                "options": {{
                    "A": "Option 1",
                    "B": "Option 2",
                    "C": "Option 3",
                    "D": "Option 4"
                }},
                "correct_answer": "A"
            }}
        ]
    }}
    """

    response = client.responses.create(
        input=prompt,
        model="openai/gpt-oss-20b",
    )

    # Extract generated text
    response_text = response.output_text

    # Convert JSON string into Python dictionary
    data = json.loads(response_text)

    questions = data["questions"]

    if len(questions) != num_questions:
        raise ValueError(
            f"Expected {num_questions} questions, "
            f"but received {len(questions)}."
        )

    for index, question in enumerate(questions, start=1):

        if not isinstance(question.get("question"), str):
            raise ValueError(f"Question {index} has an invalid question.")

        options = question.get("options")

        if not isinstance(options, dict) or set(options.keys()) != set(OPTIONS):
            raise ValueError(f"Question {index} must have options A, B, C, and D.")

        if not all(
            isinstance(options[key], str) and options[key].strip()
            for key in OPTIONS
        ):
            raise ValueError(f"Question {index} has an empty or invalid option.")

        if question.get("correct_answer") not in OPTIONS:
            raise ValueError(f"Question {index} has an invalid correct answer.")

        question["id"] = index

    return questions
