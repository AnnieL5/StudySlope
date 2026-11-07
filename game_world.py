"""game_world.py - game logic for the tile-based scrolling stage.

This module only handles *what happens* (movement, spawning, collisions).
Drawing the world is done in ui.py.
"""
import random
import pygame

from config import (
    TILE_SIZE, GRID_COLS, SCREEN_HEIGHT, PLAYER_ROW, SCROLL_SPEED,
    MOVE_COOLDOWN, SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX, TREE_CHANCE,
)


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
        self.player_col = GRID_COLS // 2
        self.facing = "right"          # "left" or "right" -> picks player image
        self.entities = []
        self.spawn_timer = 1.0
        self.move_timer = 0.0
        self.scroll_offset = 0.0       # used to scroll the background tiles

    def clear_entities(self):
        """Remove everything on screen (used when returning from a question)."""
        self.entities = []
        self.spawn_timer = 1.0

    @property
    def player_rect(self):
        return pygame.Rect(
            self.player_col * TILE_SIZE, PLAYER_ROW * TILE_SIZE,
            TILE_SIZE, TILE_SIZE,
        )

    # ------------------------------------------------------------ update
    def update(self, dt, keys, sensor_direction=0):
        """Advance the world by dt seconds.

        sensor_direction: -1 (left), 0 (none) or 1 (right) from the distance sensor.
        Returns a list of events such as ["star"] or ["tree"].
        """
        self._move_player(dt, keys, sensor_direction)

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

    def _move_player(self, dt, keys, sensor_direction=0):
        """Move one tile left/right. Keyboard wins; otherwise the sensor decides."""
        self.move_timer -= dt
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = 1
        if direction == 0:
            direction = sensor_direction

        if direction != 0:
            self.facing = "left" if direction < 0 else "right"
            if self.move_timer <= 0:
                self.player_col = max(0, min(GRID_COLS - 1, self.player_col + direction))
                self.move_timer = MOVE_COOLDOWN

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