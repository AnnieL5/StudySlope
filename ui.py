"""ui.py - everything that is drawn on screen (presentation only)."""
import math
import os
import pygame

from config import *

# ------------------------------------------------------------------ Layout
UPLOAD_BUTTON_RECT = pygame.Rect(300, 240, 300, 70)
NEXT_BUTTON_RECT = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 90, 140, 50)
CONTINUE_BUTTON_RECT = pygame.Rect(SCREEN_WIDTH // 2 - 100, 565, 200, 50)
RESTART_BUTTON_RECT = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 55)
OPTION_RECTS = [pygame.Rect(60, 210 + i * 80, 780, 68) for i in range(4)]

# ------------------------------------------------------------------ Fonts
_font_cache = {}


def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]


# ------------------------------------------------------------------ Basic helpers
def draw_text(surface, text, size, color, **position):
    """Draw text. Pass a position such as center=(x, y) or topleft=(x, y)."""
    image = get_font(size).render(text, True, color)
    rect = image.get_rect(**position)
    surface.blit(image, rect)
    return rect


def wrap_text(text, font, max_width):
    """Split text into lines that each fit inside max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_button(surface, rect, label, mouse_pos, enabled=True):
    if not enabled:
        color = BUTTON_DISABLED_COLOR
    elif rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER_COLOR
    else:
        color = BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, WHITE if enabled else GRAY, rect, 2, border_radius=12)
    draw_text(surface, label, 32, WHITE if enabled else GRAY, center=rect.center)


# ------------------------------------------------------------------ Images
assets = {}


def _fallback_player(facing):
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (90, 170, 255), surf.get_rect().inflate(-8, -8))
    eye_x = TILE_SIZE // 4 if facing == "left" else 3 * TILE_SIZE // 4
    pygame.draw.circle(surf, WHITE, (eye_x, TILE_SIZE // 3), 5)
    return surf


def _fallback_star():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    center, outer, inner = TILE_SIZE / 2, TILE_SIZE / 2 - 4, TILE_SIZE / 4.5
    points = []
    for i in range(10):
        radius = outer if i % 2 == 0 else inner
        angle = math.pi / 5 * i - math.pi / 2
        points.append((center + radius * math.cos(angle), center + radius * math.sin(angle)))
    pygame.draw.polygon(surf, YELLOW, points)
    return surf


def _fallback_tree():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, (110, 75, 40), (TILE_SIZE // 2 - 5, TILE_SIZE * 2 - 22, 10, 22))
    pygame.draw.polygon(surf, (40, 140, 70), [(TILE_SIZE // 2, 2), (4, TILE_SIZE + 10), (TILE_SIZE - 4, TILE_SIZE + 10)])
    pygame.draw.polygon(surf, (30, 120, 60), [(TILE_SIZE // 2, 35), (2, TILE_SIZE * 2 - 18), (TILE_SIZE - 2, TILE_SIZE * 2 - 18)])
    return surf


def _fallback_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((40, 48, 70))
    pygame.draw.rect(surf, (55, 65, 95), surf.get_rect(), 1)
    return surf


def _load_image(path, size, fallback):
    """Load an image and scale it to size; use the fallback if the file is missing."""
    if os.path.exists(path):
        try:
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
        except pygame.error:
            pass
    return fallback


def load_assets():
    """Call once after pygame.display.set_mode()."""
    t = TILE_SIZE
    assets["player_left"] = _load_image(PLAYER_LEFT_IMAGE, (t, t), _fallback_player("left"))
    assets["player_right"] = _load_image(PLAYER_RIGHT_IMAGE, (t, t), _fallback_player("right"))
    assets["tree"] = _load_image(TREE_IMAGE, (t, 2 * t), _fallback_tree())
    assets["star"] = _load_image(STAR_IMAGE, (t, t), _fallback_star())
    assets["background"] = _load_image(BACKGROUND_TILE_IMAGE, (t, t), _fallback_tile())


# ------------------------------------------------------------------ Screens
def draw_setup_screen(screen, status_text, status_color, next_enabled, mouse_pos):
    screen.fill(BG_COLOR)
    draw_text(screen, "StudySlope", 64, WHITE, center=(SCREEN_WIDTH // 2, 120))
    draw_button(screen, UPLOAD_BUTTON_RECT, "Upload Study Notes", mouse_pos)
    draw_text(screen, status_text, 30, status_color, center=(SCREEN_WIDTH // 2, 350))
    draw_button(screen, NEXT_BUTTON_RECT, "Next", mouse_pos, enabled=next_enabled)


def draw_generating_screen(screen):
    screen.fill(BG_COLOR)
    dots = "." * (pygame.time.get_ticks() // 400 % 4)
    draw_text(screen, "Generating questions" + dots, 48, WHITE,
              center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    draw_text(screen, "This can take a few seconds.", 28, GRAY,
              center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))


def draw_game_screen(screen, world, score, completed, total):
    # Background tiles scroll upward with the world
    tile = assets["background"]
    offset = int(world.scroll_offset)
    for row in range(GRID_ROWS + 1):
        for col in range(GRID_COLS):
            screen.blit(tile, (col * TILE_SIZE, row * TILE_SIZE - offset))

    # Trees and stars
    for entity in world.entities:
        screen.blit(assets[entity.kind], entity.rect.topleft)

    # Player (image depends on the direction they last moved)
    player_image = assets["player_left" if world.facing == "left" else "player_right"]
    screen.blit(player_image, world.player_rect.topleft)

    # Dashboard in the bottom-right corner
    panel_rect = pygame.Rect(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 90, 230, 80)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=10)
    screen.blit(panel, panel_rect.topleft)
    draw_text(screen, f"Score: {score}", 32, WHITE, topleft=(panel_rect.x + 15, panel_rect.y + 12))
    draw_text(screen, f"Questions: {completed} / {total}", 28, WHITE,
              topleft=(panel_rect.x + 15, panel_rect.y + 46))


def draw_freeze_overlay(screen, seconds_left):
    """Dim the frozen game and show a countdown before play resumes."""
    shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 110))
    screen.blit(shade, (0, 0))
    draw_text(screen, "Get ready!", 64, WHITE, center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    draw_text(screen, str(max(1, math.ceil(seconds_left))), 56, YELLOW,
              center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))


def draw_question_screen(screen, question_data, mouse_pos, selected=None, show_feedback=False):
    """Question + four options.

    show_feedback=False -> options react to hovering.
    show_feedback=True  -> correct option green, a wrong selection red,
                           plus a Continue button.
    """
    screen.fill(BG_COLOR)
    correct = question_data["correct_answer"]

    y = 40
    for line in wrap_text(question_data["question"], get_font(36), 780)[:5]:
        draw_text(screen, line, 36, WHITE, topleft=(60, y))
        y += 40

    option_font = get_font(28)
    for letter, rect in zip(OPTIONS, OPTION_RECTS):
        if show_feedback and letter == correct:
            color = GREEN
        elif show_feedback and letter == selected:
            color = RED
        elif not show_feedback and rect.collidepoint(mouse_pos):
            color = HOVER_COLOR
        else:
            color = PANEL_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

        lines = wrap_text(f"{letter}.  {question_data['options'][letter]}", option_font, rect.width - 30)[:2]
        text_y = rect.y + (rect.height - len(lines) * 30) // 2
        for line in lines:
            draw_text(screen, line, 28, WHITE, topleft=(rect.x + 15, text_y))
            text_y += 30

    if show_feedback:
        message = "Correct!" if selected == correct else "Incorrect - the right answer is in green."
        draw_text(screen, message, 28, GREEN if selected == correct else RED,
                  center=(SCREEN_WIDTH // 2, 540))
        draw_button(screen, CONTINUE_BUTTON_RECT, "Continue", mouse_pos)


def draw_finished_screen(screen, score, correct_count, total, mouse_pos):
    screen.fill(BG_COLOR)
    draw_text(screen, "Game Over!", 72, WHITE, center=(SCREEN_WIDTH // 2, 150))
    draw_text(screen, f"Final score: {score}", 44, YELLOW, center=(SCREEN_WIDTH // 2, 250))
    draw_text(screen, f"Correct answers: {correct_count} / {total}", 36, WHITE,
              center=(SCREEN_WIDTH // 2, 320))
    draw_button(screen, RESTART_BUTTON_RECT, "Play Again", mouse_pos)


def draw_sensor_debug(screen, lines):
    """Small status panel in the bottom-left corner (see SENSOR_DEBUG in config.py)."""
    panel_rect = pygame.Rect(10, SCREEN_HEIGHT - 10 - len(lines) * 22 - 12, 540, len(lines) * 22 + 12)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 190), panel.get_rect(), border_radius=8)
    screen.blit(panel, panel_rect.topleft)
    for i, line in enumerate(lines):
        draw_text(screen, line, 22, WHITE, topleft=(panel_rect.x + 10, panel_rect.y + 6 + i * 22))