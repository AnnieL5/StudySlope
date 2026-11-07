import os

# Window settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60
WINDOW_TITLE = "AI Quiz Game"

# Question settings
NUM_QUESTIONS = 10
OPTIONS = ["A", "B", "C", "D"]

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
NOTES_FILE = os.path.join(BASE_DIR, "study_notes.txt")

# Colours (R, G, B)
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GREY = (210, 210, 210)
DARK_GREY = (80, 80, 80)
BLUE = (65, 120, 220)
GREEN = (60, 170, 100)
RED = (210, 70, 70)
LIGHT_BLUE = (225, 235, 250)