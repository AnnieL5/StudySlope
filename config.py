"""config.py - shared settings for the whole game.

NOTE: if question_manager.py or other modules import path/colour names from
your existing config.py (e.g. a questions-file constant), keep those names
and just add the new constants below to your file.
"""
import os

# ---------------------------------------------------------------- Window
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60
WINDOW_TITLE = "AI Quiz Game"

# ---------------------------------------------------------------- Quiz
NUM_QUESTIONS = 10
OPTIONS = ["A", "B", "C", "D"]

# ---------------------------------------------------------------- Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Image placeholders: put your artwork at these paths.
# If a file is missing, ui.py draws a simple coloured shape instead,
# so the game always runs.
PLAYER_LEFT_IMAGE = os.path.join(ASSETS_DIR, "player_left.png")
PLAYER_RIGHT_IMAGE = os.path.join(ASSETS_DIR, "player_right.png")
TREE_IMAGE = os.path.join(ASSETS_DIR, "tree.png")          # 1 tile wide x 2 tall
STAR_IMAGE = os.path.join(ASSETS_DIR, "star.png")          # 1 x 1 tile
BACKGROUND_TILE_IMAGE = os.path.join(ASSETS_DIR, "background_tile.png")  # 1 x 1 tile

# ---------------------------------------------------------------- Grid
TILE_SIZE = 50
GRID_COLS = SCREEN_WIDTH // TILE_SIZE    # 18
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE   # 13
PLAYER_ROW = GRID_ROWS // 3              # player sits in the top third (row 4)

# ---------------------------------------------------------------- Gameplay
SCROLL_SPEED = 180           # pixels per second that objects rise
MOVE_COOLDOWN = 0.12         # seconds between tile steps while a key is held
SPAWN_INTERVAL_MIN = 0.5     # seconds between spawns (random in this range)
SPAWN_INTERVAL_MAX = 1.1
TREE_CHANCE = 0.35           # probability a spawned object is a tree
STARS_PER_QUESTION = 3       # collecting this many stars triggers a question
STAR_POINTS = 10
CORRECT_POINTS = 50

# ---------------------------------------------------------------- Distance sensor
USE_SENSOR = True            # False = keyboard only (no serial port is opened)
SENSOR_PORT = "COM12"         # e.g. "COM3" on Windows, "/dev/ttyACM0" on Linux
SENSOR_BAUD_RATE = 9600
SENSOR_THRESHOLD = 10.0      # distance above this -> move right, below -> move left
SENSOR_DEADZONE = 1.0        # no movement within threshold +/- deadzone (stops jitter)
SENSOR_AVG_READINGS = 3      # rolling average over the last N readings (smoother)
SENSOR_TIMEOUT = 0.5         # seconds without a reading before the player stops

# ---------------------------------------------------------------- Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 70)
BG_COLOR = (30, 34, 48)
PANEL_COLOR = (55, 60, 80)
HOVER_COLOR = (80, 90, 120)
BUTTON_COLOR = (70, 110, 200)
BUTTON_HOVER_COLOR = (95, 135, 230)
BUTTON_DISABLED_COLOR = (70, 70, 80)
GREEN = (60, 170, 90)
RED = (200, 70, 70)
YELLOW = (250, 210, 60)