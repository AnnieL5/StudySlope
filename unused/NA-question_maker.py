
# import os
# import json
# import dotenv
# from groq import Groq

# dotenv.load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# def generate_questions(user_information, num_questions=10):

#     prompt = f"""
#     You are an expert tutor creating multiple-choice questions.

#     Generate exactly {num_questions} different questions
#     based on the study notes below.

#     Requirements:
#     - Each question must have exactly 4 options.
#     - Label options A, B, C, D.
#     - Only one option must be correct.
#     - Make incorrect options plausible.
#     - Cover different concepts from the notes.
#     - Do not repeat questions.

#     Return ONLY valid JSON in this format:

#     {{
#         "questions": [
#             {{
#                 "id": 1,
#                 "question": "Question text",
#                 "options": {{
#                     "A": "Option A",
#                     "B": "Option B",
#                     "C": "Option C",
#                     "D": "Option D"
#                 }},
#                 "correct_answer": "A"
#             }}
#         ]
#     }}

#     Study notes:
#     {user_information}
#     """

#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Generate accurate educational multiple-choice questions. Return valid JSON only."
#             },
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         temperature=0.7,
#         max_tokens=3000,
#         response_format={"type": "json_object"}
#     )

#     result = response.choices[0].message.content

#     # Convert JSON string into Python dictionary
#     data = json.loads(result)

#     questions = data["questions"]

#     # Validate questions
#     for i, question in enumerate(questions):

#         if not all(key in question for key in
#                    ["question", "options", "correct_answer"]):
#             raise ValueError(f"Question {i+1} is missing required fields.")

#         if set(question["options"].keys()) != {"A", "B", "C", "D"}:
#             raise ValueError(f"Question {i+1} must have four options.")

#         if question["correct_answer"] not in ["A", "B", "C", "D"]:
#             raise ValueError(f"Question {i+1} has an invalid answer.")

#         question["id"] = i + 1

#     if len(questions) != num_questions:
#         raise ValueError(
#             f"Expected {num_questions} questions, got {len(questions)}."
#         )

#     # Save all questions to JSON
#     with open("questions.json", "w", encoding="utf-8") as file:
#         json.dump(
#             {"questions": questions},
#             file,
#             indent=4,
#             ensure_ascii=False
#         )

#     print(f"Successfully saved {len(questions)} questions!")

#     return questions
