"""main.py - game loop, states, and input handling.

States:
    setup       -> upload notes, press Next
    generating  -> questions are generated in a background thread
    playing     -> tile game: move left/right, hit trees / collect stars
    question    -> a question is shown (triggered by a tree or 3 stars)
    feedback    -> wrong answer: red/green highlight + Continue button
    finished    -> all questions answered
"""
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog

import pygame

from config import *
from game_world import GameWorld
from question_generator import generate_questions
from question_manager import save_questions, load_questions, get_question_for_stage
import ui
from sensor import DistanceSensor


def pick_study_file():
    """Open a native file dialog and return the chosen path ('' if cancelled)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select your study notes",
        filetypes=[("Text files", "*.txt")],
    )
    root.destroy()
    return path


def generate_questions_background(user_information, result_queue):
    """Runs in a background thread so the Pygame window doesn't freeze.

    It reports back through the queue: ("ok", None) or ("error", message).
    """
    try:
        questions = generate_questions(user_information, NUM_QUESTIONS)
        save_questions(questions)
        result_queue.put(("ok", None))
    except Exception as error:
        result_queue.put(("error", str(error)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    ui.load_assets()

    sensor = DistanceSensor()   # opens the serial port (keyboard-only if that fails)
    world = GameWorld()
    generation_queue = queue.Queue()

    # ---- Game data
    game_state = "setup"
    user_information = ""
    status_text = "No study notes uploaded yet"
    status_color = GRAY
    questions = []
    current_question = None
    selected_answer = None
    score = 0
    completed = 0
    correct_count = 0
    stars_collected = 0   # stars collected since the last question
    freeze_timer = 0.0    # seconds left in the pause after a question

    def start_question():
        nonlocal game_state, current_question, selected_answer, stars_collected
        current_question = get_question_for_stage(questions, completed + 1)
        selected_answer = None
        stars_collected = 0
        game_state = "question"

    def finish_or_resume():
        """After a question: end the game, or return to the (frozen) tile game.

        The tree/star that was hit is already gone (GameWorld removes it on
        collision); everything else stays where it was.
        """
        nonlocal game_state, freeze_timer
        if completed >= len(questions):
            game_state = "finished"
        else:
            freeze_timer = FREEZE_DURATION
            game_state = "freeze"

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000, 0.05)   # seconds since last frame
        mouse_pos = pygame.mouse.get_pos()

        # ------------------------------------------------ Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "setup":
                    if ui.UPLOAD_BUTTON_RECT.collidepoint(event.pos):
                        path = pick_study_file()
                        if path:
                            try:
                                with open(path, "r", encoding="utf-8", errors="replace") as f:
                                    text = f.read()
                                if text.strip():
                                    user_information = text
                                    status_text = f"Done! Uploaded: {os.path.basename(path)}"
                                    status_color = GREEN
                                else:
                                    user_information = ""
                                    status_text = "That file is empty. Try another one."
                                    status_color = RED
                            except OSError:
                                user_information = ""
                                status_text = "Could not read that file."
                                status_color = RED
                    elif ui.NEXT_BUTTON_RECT.collidepoint(event.pos) and user_information:
                        game_state = "generating"
                        thread = threading.Thread(
                            target=generate_questions_background,
                            args=(user_information, generation_queue),
                            daemon=True,
                        )
                        thread.start()

                elif game_state == "question":
                    for letter, rect in zip(OPTIONS, ui.OPTION_RECTS):
                        if rect.collidepoint(event.pos):
                            selected_answer = letter
                            completed += 1
                            if letter == current_question["correct_answer"]:
                                score += CORRECT_POINTS
                                correct_count += 1
                                finish_or_resume()          # correct -> continue
                            else:
                                game_state = "feedback"     # wrong -> show answer
                            break

                elif game_state == "feedback":
                    if ui.CONTINUE_BUTTON_RECT.collidepoint(event.pos):
                        finish_or_resume()

                elif game_state == "finished":
                    if ui.RESTART_BUTTON_RECT.collidepoint(event.pos):
                        world.reset()
                        questions = []
                        user_information = ""
                        status_text = "No study notes uploaded yet"
                        status_color = GRAY
                        score = completed = correct_count = stars_collected = 0
                        game_state = "setup"

        # ------------------------------------------------ Update
        sensor.update()   # drain serial data every frame, whatever the state

        if game_state == "generating":
            try:
                result, message = generation_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if result == "ok":
                    questions = load_questions()
                    world.reset()
                    score = completed = correct_count = stars_collected = 0
                    game_state = "playing"
                else:
                    status_text = f"Generation failed: {message[:60]}"
                    status_color = RED
                    game_state = "setup"

        elif game_state == "playing":
            keys = pygame.key.get_pressed()
            for kind in world.update(dt, keys, sensor.get_target_ratio()):
                if kind == "star":
                    score += STAR_POINTS
                    stars_collected += 1
                    if stars_collected >= STARS_PER_QUESTION:
                        start_question()
                        break
                elif kind == "tree":
                    start_question()
                    break

        elif game_state == "freeze":
            # The world is NOT updated here, so everything stays frozen.
            freeze_timer -= dt
            if freeze_timer <= 0:
                game_state = "playing"

        # ------------------------------------------------ Draw
        if game_state == "setup":
            ui.draw_setup_screen(screen, status_text, status_color, bool(user_information), mouse_pos)
        elif game_state == "generating":
            ui.draw_generating_screen(screen)
        elif game_state == "playing":
            ui.draw_game_screen(screen, world, score, completed, len(questions))
        elif game_state == "freeze":
            ui.draw_game_screen(screen, world, score, completed, len(questions))
            ui.draw_freeze_overlay(screen, freeze_timer)
        elif game_state == "question":
            ui.draw_question_screen(screen, current_question, mouse_pos)
        elif game_state == "feedback":
            ui.draw_question_screen(screen, current_question, mouse_pos,
                                    selected=selected_answer, show_feedback=True)
        elif game_state == "finished":
            ui.draw_finished_screen(screen, score, correct_count, len(questions), mouse_pos)

        # if SENSOR_DEBUG and game_state in ("setup", "playing"):
        #     ui.draw_sensor_debug(screen, sensor.debug_lines())

        pygame.display.flip()

    sensor.close()
    pygame.quit()


if __name__ == "__main__":
    main()
