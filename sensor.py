"""sensor.py - reads the Arduino distance sensor and maps it to a grid column.

Requires pyserial:   pip install pyserial
(The package is installed as "pyserial" but imported as "serial".)

If pyserial is missing or the port can't be opened, the game still runs
with keyboard control only.
"""
import time
from collections import deque

from config import (
    USE_SENSOR, SENSOR_PORT, SENSOR_BAUD_RATE, SENSOR_MIN_DIST,
    SENSOR_MAX_DIST, SENSOR_AVG_READINGS, SENSOR_TIMEOUT, GRID_COLS,
)

try:
    import serial
except ImportError:
    serial = None


class DistanceSensor:
    def __init__(self):
        # deque(maxlen=3) automatically drops the oldest reading when a new
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

    def get_target_column(self):
        """Map the smoothed distance to a grid column, or None if no fresh data.

        SENSOR_MIN_DIST -> column 0 (far left)
        SENSOR_MAX_DIST -> last column (far right)
        halfway between -> middle column
        """
        average = self.average_distance
        if average is None:
            return None
        if time.monotonic() - self.last_reading_time > SENSOR_TIMEOUT:
            return None   # sensor went quiet, so the player holds still

        span = SENSOR_MAX_DIST - SENSOR_MIN_DIST
        if span <= 0:
            return None
        ratio = (average - SENSOR_MIN_DIST) / span
        ratio = max(0.0, min(1.0, ratio))        # clamp to 0..1
        return round(ratio * (GRID_COLS - 1))

    def close(self):
        if self.arduino is not None:
            try:
                self.arduino.close()
            except Exception:
                pass
            self.arduino = None