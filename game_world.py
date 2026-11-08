"""game_world.py - game logic for the tile-based scrolling stage.

This module only handles *what happens* (movement, spawning, collisions).
Drawing the world is done in ui.py.
"""
import random
import pygame

from config import (
    TILE_SIZE, GRID_COLS, SCREEN_HEIGHT, PLAYER_ROW, SCROLL_SPEED,
    SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX, TREE_CHANCE,
)

# ---- Player movement (from the old sensor prototype)
SMOOTHING = 0.15      # each frame (at 60 FPS) the player covers 15% of the gap to the target
KEY_SPEED = 400       # pixels per second the target moves when using the keyboard

WORLD_WIDTH = GRID_COLS * TILE_SIZE
MAX_PLAYER_X = WORLD_WIDTH - TILE_SIZE


class Entity:
    """A tree (1 wide x 2 tall) or a star (1 x 1) on the grid."""

    def __init__(self, kind, col, y):
        self.kind = kind          # "tree" or "star"
        self.col = col            # grid column (whole number)
        self.y = float(y)         # vertical position in pixels (smooth movement)
        self.height_tiles = 2 if kind == "tree" else 1

    @property
    def rect(self):
        return pygame.Rect(
            self.col * TILE_SIZE,
            int(self.y),
            TILE_SIZE,
            self.height_tiles * TILE_SIZE,
        )


class GameWorld:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_x = MAX_PLAYER_X / 2     # smooth pixel position
        self.target_x = self.player_x        # where the player is gliding to
        self.facing = "right"                # "left" or "right" -> picks player image
        self.entities = []
        self.spawn_timer = 1.0
        self.scroll_offset = 0.0             # used to scroll the background tiles

    def clear_entities(self):
        """Remove everything on screen (used when returning from a question)."""
        self.entities = []
        self.spawn_timer = 1.0

    @property
    def player_col(self):
        """Grid column the player is mostly in (kept so other code still works)."""
        col = int((self.player_x + TILE_SIZE / 2) // TILE_SIZE)
        return max(0, min(GRID_COLS - 1, col))

    @property
    def player_rect(self):
        return pygame.Rect(
            round(self.player_x), PLAYER_ROW * TILE_SIZE,
            TILE_SIZE, TILE_SIZE,
        )

    # ------------------------------------------------------------ update
    def update(self, dt, keys, sensor_ratio=None):
        """Advance the world by dt seconds.

        sensor_ratio: 0.0 (far left) to 1.0 (far right) from the distance
                      sensor, or None if there is no fresh sensor data.
        Returns a list of events such as ["star"] or ["tree"].
        """
        self._move_player(dt, keys, sensor_ratio)

        # Scroll everything upward
        self.scroll_offset = (self.scroll_offset + SCROLL_SPEED * dt) % TILE_SIZE
        for entity in self.entities:
            entity.y -= SCROLL_SPEED * dt

        # Drop entities that have fully left the top of the screen
        self.entities = [
            e for e in self.entities
            if e.y + e.height_tiles * TILE_SIZE > 0
        ]

        # Spawn new ones below the screen
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
            self._spawn_entity()

        return self._check_collisions()

    def _move_player(self, dt, keys, sensor_ratio=None):
        """Glide the player toward a target x position.

        Keyboard wins and nudges the target left/right. Otherwise the sensor
        sets the target directly. Either way the player eases toward the
        target a little each frame, exactly like the old prototype.
        """
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = 1

        if direction != 0:
            self.target_x += direction * KEY_SPEED * dt
        elif sensor_ratio is not None:
            self.target_x = sensor_ratio * MAX_PLAYER_X
        self.target_x = max(0.0, min(MAX_PLAYER_X, self.target_x))

        # Same easing as the old code, adjusted so it behaves the same at any frame rate
        factor = 1 - (1 - SMOOTHING) ** (dt * 60)
        old_x = self.player_x
        self.player_x += (self.target_x - self.player_x) * factor
        self.player_x = max(0.0, min(MAX_PLAYER_X, self.player_x))

        moved = self.player_x - old_x
        if moved < -0.1:
            self.facing = "left"
        elif moved > 0.1:
            self.facing = "right"

    def _spawn_entity(self):
        kind = "tree" if random.random() < TREE_CHANCE else "star"
        col = random.randrange(GRID_COLS)
        new_entity = Entity(kind, col, SCREEN_HEIGHT)   # just below the screen

        # Don't spawn on top of (or touching) something already in that column
        padding = new_entity.rect.inflate(0, TILE_SIZE)
        if any(padding.colliderect(e.rect) for e in self.entities):
            return
        self.entities.append(new_entity)

    def _check_collisions(self):
        events = []
        player = self.player_rect
        for entity in self.entities[:]:
            if entity.rect.colliderect(player):
                events.append(entity.kind)
                self.entities.remove(entity)   # stars (and trees) vanish when hit
        return events
