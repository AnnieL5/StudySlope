"""sensor.py - reads the Arduino distance sensor and maps it to a position.

Requires pyserial:   pip install pyserial
(The package is installed as "pyserial" but imported as "serial".)

If pyserial is missing or the port can't be opened, the game still runs
with keyboard control only.

Mapping (same as the old prototype):
    position_px = (distance - 4) * 50   across an 800px window with a 50px player
That means 4 cm is the far left and (800 - 50) / 50 = 15 cm further (19 cm)
is the far right. Here the result is returned as a 0..1 ratio so it works
with any window size.
"""
import time
from collections import deque

from config import (
    USE_SENSOR, SENSOR_PORT, SENSOR_BAUD_RATE,
    SENSOR_AVG_READINGS, SENSOR_TIMEOUT,
)

try:
    import serial
except ImportError:
    serial = None

# ---- Values taken from the old prototype
OLD_OFFSET_CM = 4                                   # reading that counts as "far left"
OLD_PIXELS_PER_CM = 50
OLD_WINDOW_WIDTH = 800
OLD_PLAYER_WIDTH = 50
SENSOR_SPAN_CM = (OLD_WINDOW_WIDTH - OLD_PLAYER_WIDTH) / OLD_PIXELS_PER_CM   # 15 cm


class DistanceSensor:
    def __init__(self):
        # deque(maxlen=N) automatically drops the oldest reading when a new
        # one is added, which gives us a cheap rolling average.
        self.readings = deque(maxlen=SENSOR_AVG_READINGS)
        self.last_reading_time = 0.0
        self.arduino = None

        if not USE_SENSOR:
            return
        if serial is None:
            print("Sensor disabled: pyserial is not installed (pip install pyserial).")
            return
        try:
            # A tiny timeout keeps readline() from freezing the game loop.
            self.arduino = serial.Serial(SENSOR_PORT, SENSOR_BAUD_RATE, timeout=0.01)
        except serial.SerialException as error:
            print(f"Sensor disabled: could not open {SENSOR_PORT} ({error}).")

    @property
    def connected(self):
        return self.arduino is not None

    def update(self):
        """Read everything the Arduino has sent since the last frame.

        Call once per frame, in every game state, so old data never piles up.
        """
        if self.arduino is None:
            return
        try:
            while self.arduino.in_waiting:
                line = self.arduino.readline().decode(errors="ignore").strip()
                try:
                    self.readings.append(float(line))
                    self.last_reading_time = time.monotonic()
                except ValueError:
                    pass   # partial or garbled line - ignore it
        except (serial.SerialException, OSError):
            print("Sensor disconnected.")
            self.close()

    @property
    def average_distance(self):
        if not self.readings:
            return None
        return sum(self.readings) / len(self.readings)

    def get_target_ratio(self):
        """Return 0.0 (far left) to 1.0 (far right), or None if no fresh data."""
        average = self.average_distance
        if average is None:
            return None
        if time.monotonic() - self.last_reading_time > SENSOR_TIMEOUT:
            return None   # sensor went quiet, so the player holds still

        ratio = (average - OLD_OFFSET_CM) / SENSOR_SPAN_CM
        return max(0.0, min(1.0, ratio))

    def close(self):
        if self.arduino is not None:
            try:
                self.arduino.close()
            except Exception:
                pass
            self.arduino = None
