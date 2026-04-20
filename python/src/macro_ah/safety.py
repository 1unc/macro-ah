"""Abort-Wache: erkennt Mausbewegung und Esc-Druck waehrend der Ausfuehrung."""

from __future__ import annotations

import time

import keyboard
import pyautogui


MOUSE_ABORT_TOLERANCE: int = 60


class Aborted(Exception):
    """Kontrollierter Abbruch durch Nutzer-Signal."""


class AbortGuard:
    def __init__(self, tolerance: int = MOUSE_ABORT_TOLERANCE) -> None:
        self.tolerance = tolerance
        self.baseline: tuple[int, int] = tuple(pyautogui.position())  # type: ignore[assignment]

    def reset_baseline(self) -> None:
        self.baseline = tuple(pyautogui.position())  # type: ignore[assignment]

    def check(self) -> None:
        cur = pyautogui.position()
        if abs(cur[0] - self.baseline[0]) > self.tolerance or abs(cur[1] - self.baseline[1]) > self.tolerance:
            raise Aborted("Mausbewegung erkannt")
        if keyboard.is_pressed("esc"):
            raise Aborted("Esc gedrueckt")

    def sleep(self, seconds: float) -> None:
        end = time.time() + seconds
        while True:
            remaining = end - time.time()
            if remaining <= 0:
                return
            self.check()
            time.sleep(min(0.05, remaining))

    def move_to(self, pos: tuple[int, int], duration: float = 0.08) -> None:
        pyautogui.moveTo(pos[0], pos[1], duration=duration)
        self.reset_baseline()

    def click(
        self,
        pos: tuple[int, int],
        button: str = "left",
        before: float = 0.12,
        after: float = 0.18,
    ) -> None:
        self.sleep(before)
        self.move_to(pos)
        pyautogui.click(button=button)
        self.reset_baseline()
        self.sleep(after)

    def type_text(self, text: str) -> None:
        self.check()
        pyautogui.typewrite(text, interval=0.03)
        self.reset_baseline()

    def press_key(self, key: str) -> None:
        self.check()
        keyboard.press_and_release(key)
