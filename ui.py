import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    BLACK,
    GREY,
    DARK_GREY,
    BLUE,
    GREEN,
    RED,
    LIGHT_BLUE
)


def draw_text(screen, text, font, colour, x, y, max_width):
    """Draw text with automatic line wrapping."""

    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    for line in lines:
        rendered = font.render(line, True, colour)
        screen.blit(rendered, (x, y))
        y += font.get_linesize()

    return y


def draw_button(screen, rect, text, font, colour=BLUE):
    pygame.draw.rect(screen, colour, rect, border_radius=10)
    pygame.draw.rect(screen, DARK_GREY, rect, 2, border_radius=10)

    rendered = font.render(text, True, WHITE)
    text_rect = rendered.get_rect(center=rect.center)

    screen.blit(rendered, text_rect)


def draw_setup_screen(screen, title_font, font, small_font, selected_file, status):

    screen.fill(WHITE)

    title = title_font.render("AI Quiz Game", True, BLACK)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))

    instructions = font.render(
        "Load your study notes and generate your questions.",
        True,
        DARK_GREY
    )
    screen.blit(instructions, instructions.get_rect(center=(450, 190)))

    load_rect = pygame.Rect(300, 270, 300, 60)
    draw_button(screen, load_rect, "Load Study Notes", font)

    if selected_file:
        filename = selected_file.split("/")[-1].split("\\")[-1]
        draw_text(
            screen,
            f"Selected: {filename}",
            small_font,
            BLACK,
            250,
            350,
            400
        )
    else:
        message = small_font.render("No file selected", True, DARK_GREY)
        screen.blit(message, message.get_rect(center=(450, 370)))

    generate_rect = pygame.Rect(300, 430, 300, 60)
    draw_button(screen, generate_rect, "Generate Questions", font, GREEN)

    if status:
        status_text = small_font.render(status, True, DARK_GREY)
        screen.blit(status_text, status_text.get_rect(center=(450, 530)))

    return load_rect, generate_rect


def draw_generating_screen(screen, title_font, font):

    screen.fill(WHITE)

    title = title_font.render("Generating Questions...", True, BLACK)
    screen.blit(title, title.get_rect(center=(450, 250)))

    message = font.render(
        "Please wait while AI creates your quiz.",
        True,
        DARK_GREY
    )
    screen.blit(message, message.get_rect(center=(450, 330)))


def draw_quiz_screen(
    screen,
    question_data,
    stage,
    total_questions,
    score,
    title_font,
    font,
    small_font,
    feedback
):

    screen.fill(WHITE)

    # Stage and score
    heading = title_font.render(
        f"Stage {stage}/{total_questions}",
        True,
        BLACK
    )
    screen.blit(heading, (50, 35))

    score_text = font.render(f"Score: {score}", True, DARK_GREY)
    screen.blit(score_text, (720, 45))

    # Question
    y = draw_text(
        screen,
        question_data["question"],
        title_font,
        BLACK,
        60,
        120,
        780
    )

    # Answer options
    option_rects = {}

    option_y = max(240, y + 30)

    for letter in ["A", "B", "C", "D"]:

        rect = pygame.Rect(100, option_y, 700, 65)

        pygame.draw.rect(screen, LIGHT_BLUE, rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, rect, 2, border_radius=10)

        draw_text(
            screen,
            f"{letter}. {question_data['options'][letter]}",
            font,
            BLACK,
            rect.x + 15,
            rect.y + 15,
            rect.width - 30
        )

        option_rects[letter] = rect
        option_y += 85

    if feedback:
        feedback_colour = GREEN if feedback == "Correct!" else RED

        message = font.render(feedback, True, feedback_colour)
        screen.blit(message, message.get_rect(center=(450, 605)))

    return option_rects


def draw_finished_screen(screen, title_font, font, score, total_questions):

    screen.fill(WHITE)

    title = title_font.render("Quiz Completed!", True, GREEN)
    screen.blit(title, title.get_rect(center=(450, 220)))

    result = font.render(
        f"Your score: {score}/{total_questions}",
        True,
        BLACK
    )
    screen.blit(result, result.get_rect(center=(450, 320)))

    restart_rect = pygame.Rect(300, 420, 300, 65)
    draw_button(screen, restart_rect, "Play Again", font, BLUE)

    return restart_rect