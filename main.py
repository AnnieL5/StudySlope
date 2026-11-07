import pygame
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import os

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
    NUM_QUESTIONS,
    NOTES_FILE
)

from question_generator import generate_questions
from question_manager import (
    save_questions,
    load_questions,
    get_question_for_stage
)

from ui import (
    draw_setup_screen,
    draw_generating_screen,
    draw_quiz_screen,
    draw_finished_screen
)


# -----------------------------
# INITIALIZATION
# -----------------------------

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Arial", 32, bold=True)
font = pygame.font.SysFont("Arial", 23)
small_font = pygame.font.SysFont("Arial", 18)


# -----------------------------
# GAME VARIABLES
# -----------------------------

game_state = "setup"

selected_file = None
user_information = ""

questions = []

current_stage = 1
score = 0

feedback = ""
status = ""

# Used to receive results from the background thread
generation_queue = queue.Queue()

running = True


# -----------------------------
# FILE INPUT
# -----------------------------

def select_study_file():

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Study Notes",
        filetypes=[
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    return file_path


def read_study_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------
# QUESTION GENERATION
# -----------------------------

def generate_questions_background(notes):

    try:
        generated_questions = generate_questions(
            notes,
            NUM_QUESTIONS
        )

        save_questions(generated_questions)

        generation_queue.put(("success", None))

    except Exception as error:

        generation_queue.put(("error", str(error)))


def start_question_generation():

    global game_state

    game_state = "generating"

    thread = threading.Thread(
        target=generate_questions_background,
        args=(user_information,),
        daemon=True
    )

    thread.start()


# -----------------------------
# RESET GAME
# -----------------------------

def reset_game():

    global game_state
    global current_stage
    global score
    global feedback

    game_state = "setup"

    current_stage = 1
    score = 0
    feedback = ""


# -----------------------------
# MAIN GAME LOOP
# -----------------------------

while running:

    clock.tick(FPS)

    # -------------------------
    # CHECK QUESTION GENERATION
    # -------------------------

    if game_state == "generating" and not generation_queue.empty():

        result, error_message = generation_queue.get()

        if result == "success":

            try:
                questions = load_questions()

                current_stage = 1
                score = 0
                feedback = ""

                game_state = "quiz"

            except Exception as error:

                game_state = "setup"
                status = f"Could not load questions: {error}"

        else:

            game_state = "setup"
            status = f"Generation failed: {error_message}"


    # -------------------------
    # HANDLE EVENTS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            mouse_position = event.pos

            # =========================
            # SETUP SCREEN
            # =========================

            if game_state == "setup":

                load_rect, generate_rect = draw_setup_screen(
                    screen,
                    title_font,
                    font,
                    small_font,
                    selected_file,
                    status
                )

                # Load study notes
                if load_rect.collidepoint(mouse_position):

                    file_path = select_study_file()

                    if file_path:

                        try:
                            user_information = read_study_file(file_path)
                            selected_file = file_path
                            status = "Study notes loaded successfully."

                        except Exception as error:
                            status = f"Could not read file: {error}"

                # Generate questions
                elif generate_rect.collidepoint(mouse_position):

                    if not user_information.strip():

                        status = "Please load your study notes first."

                    else:

                        status = ""
                        start_question_generation()


            # =========================
            # QUIZ SCREEN
            # =========================

            elif game_state == "quiz":

                question_data = get_question_for_stage(
                    questions,
                    current_stage
                )

                if question_data:

                    option_rects = draw_quiz_screen(
                        screen,
                        question_data,
                        current_stage,
                        len(questions),
                        score,
                        title_font,
                        font,
                        small_font,
                        feedback
                    )

                    for letter, rect in option_rects.items():

                        if rect.collidepoint(mouse_position):

                            correct_answer = question_data["correct_answer"]

                            if letter == correct_answer:

                                score += 1
                                feedback = "Correct!"

                                current_stage += 1

                                if current_stage > len(questions):
                                    game_state = "finished"

                            else:

                                feedback = "Incorrect! Try again."


            # =========================
            # FINISHED SCREEN
            # =========================

            elif game_state == "finished":

                restart_rect = draw_finished_screen(
                    screen,
                    title_font,
                    font,
                    score,
                    len(questions)
                )

                if restart_rect.collidepoint(mouse_position):

                    reset_game()


    # -------------------------
    # DRAW CURRENT SCREEN
    # -------------------------

    if game_state == "setup":

        draw_setup_screen(
            screen,
            title_font,
            font,
            small_font,
            selected_file,
            status
        )

    elif game_state == "generating":

        draw_generating_screen(
            screen,
            title_font,
            font
        )

    elif game_state == "quiz":

        question_data = get_question_for_stage(
            questions,
            current_stage
        )

        if question_data:

            draw_quiz_screen(
                screen,
                question_data,
                current_stage,
                len(questions),
                score,
                title_font,
                font,
                small_font,
                feedback
            )

    elif game_state == "finished":

        draw_finished_screen(
            screen,
            title_font,
            font,
            score,
            len(questions)
        )

    pygame.display.flip()


# -----------------------------
# QUIT
# -----------------------------

pygame.quit()