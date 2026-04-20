"""Bildschirm-Analyse, Kalibrierungs-Dialog, Preis-Dialog, Split- und Listing-Phase."""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import messagebox

import keyboard
import mss
import pyautogui
from PIL import Image, ImageStat

from .config import CALIBRATION_STEPS, Config, Point
from .grid import (
    EMPTY_STDDEV_THRESHOLD,
    SACRIFICE_SLOT_INDEX,
    build_slot_grid,
    is_slot_empty_from_stddev,
    stddev_average,
)
from .safety import AbortGuard


def grab_screen_pil() -> Image.Image:
    with mss.mss() as sct:
        mon = sct.monitors[1]
        raw = sct.grab(mon)
    return Image.frombytes("RGB", raw.size, raw.rgb)


def is_slot_empty(
    img: Image.Image,
    pos: tuple[int, int],
    radius: int = 6,
    threshold: float = EMPTY_STDDEV_THRESHOLD,
) -> bool:
    x, y = pos
    crop = img.crop((x - radius, y - radius, x + radius + 1, y + radius + 1))
    stat = ImageStat.Stat(crop)
    return is_slot_empty_from_stddev(stddev_average(list(stat.stddev)), threshold)


def calibrate_dialog() -> Config | None:
    points: dict[str, Point] = {}

    root = tk.Tk()
    root.title("Macro-ah Kalibrierung")
    root.geometry("440x160")
    root.attributes("-topmost", True)

    label = tk.Label(root, text="", font=("Segoe UI", 11), wraplength=400, justify="left")
    label.pack(pady=14, padx=12)

    status = tk.Label(root, text=f"Schritt 1/{len(CALIBRATION_STEPS)}", font=("Segoe UI", 9))
    status.pack()

    tk.Label(
        root,
        text="Maus ueber die Stelle, dann LEERTASTE druecken. Esc = Abbruch.",
        font=("Segoe UI", 9),
        fg="#666",
    ).pack(pady=6)

    state: dict[str, int | bool] = {"index": 0, "done": False, "aborted": False}

    def update_label() -> None:
        idx = int(state["index"])
        _, desc = CALIBRATION_STEPS[idx]
        label.config(text=desc)
        status.config(text=f"Schritt {idx + 1}/{len(CALIBRATION_STEPS)}")

    def poll() -> None:
        if state["aborted"] or state["done"]:
            return
        if keyboard.is_pressed("esc"):
            state["aborted"] = True
            root.destroy()
            return
        if keyboard.is_pressed("space"):
            idx = int(state["index"])
            key, _ = CALIBRATION_STEPS[idx]
            pos = pyautogui.position()
            points[key] = Point(x=int(pos[0]), y=int(pos[1]))
            state["index"] = idx + 1
            while keyboard.is_pressed("space"):
                root.update()
                time.sleep(0.04)
            if int(state["index"]) >= len(CALIBRATION_STEPS):
                state["done"] = True
                root.destroy()
                return
            update_label()
        root.after(30, poll)

    update_label()
    root.after(50, poll)
    root.mainloop()

    if state["aborted"]:
        return None
    return Config(points=points)


def ask_price() -> float | None:
    result: dict[str, float] = {}

    root = tk.Tk()
    root.title("Macro-ah")
    root.geometry("340x190")
    root.attributes("-topmost", True)

    tk.Label(root, text="Preis pro Item", font=("Segoe UI", 11)).pack(pady=(16, 4))
    price_var = tk.StringVar(value="1.20")
    entry = tk.Entry(root, textvariable=price_var, font=("Segoe UI", 11), justify="center")
    entry.pack(pady=4)
    entry.focus_set()
    entry.select_range(0, tk.END)

    def on_ok(event: object = None) -> None:
        try:
            result["price"] = float(price_var.get().replace(",", "."))
            root.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Preis ungueltig. Beispiel: 1.20")

    tk.Button(root, text="OK", width=14, command=on_ok).pack(pady=10)
    tk.Label(
        root,
        text="Hotkey nach OK: Strg+Leertaste",
        font=("Segoe UI", 9),
        fg="#666",
    ).pack()

    root.bind("<Return>", on_ok)
    root.mainloop()
    return result.get("price")


def split_phase(cfg: Config, guard: AbortGuard) -> None:
    grid = build_slot_grid(cfg.point("inv_top_left"), cfg.point("inv_bottom_right"))

    guard.sleep(0.3)
    guard.press_key("e")
    guard.sleep(0.45)

    img = grab_screen_pil()
    source_idx: int | None = None
    for i, pos in enumerate(grid):
        if i == SACRIFICE_SLOT_INDEX:
            continue
        if not is_slot_empty(img, pos):
            source_idx = i
            break
    if source_idx is None:
        guard.press_key("e")
        raise RuntimeError("Kein Stack im Inventar gefunden.")

    guard.click(grid[source_idx], "left", before=0.1, after=0.22)

    drag_targets = [grid[i] for i in range(len(grid)) if i != SACRIFICE_SLOT_INDEX]

    guard.move_to(drag_targets[0])
    pyautogui.mouseDown(button="right")
    try:
        for pos in drag_targets[1:]:
            guard.check()
            pyautogui.moveTo(pos[0], pos[1], duration=0.025)
            guard.reset_baseline()
    finally:
        pyautogui.mouseUp(button="right")

    guard.sleep(0.25)

    guard.click(grid[SACRIFICE_SLOT_INDEX], "left", before=0.1, after=0.25)

    guard.press_key("e")
    guard.sleep(0.5)


def open_ah(guard: AbortGuard) -> None:
    guard.press_key("t")
    guard.sleep(0.35)
    guard.type_text("/ah")
    guard.sleep(0.15)
    guard.press_key("enter")
    guard.sleep(0.9)


def list_one(
    guard: AbortGuard,
    cfg: Config,
    slot_pos: tuple[int, int],
    price_str: str,
) -> None:
    guard.click(cfg.point("ah_create_btn"),   before=0.12, after=0.28)
    guard.click(slot_pos,                      before=0.1,  after=0.28)
    guard.click(cfg.point("ah_green_check"),  before=0.1,  after=0.28)

    guard.click(cfg.point("ah_price_field"),  before=0.1,  after=0.15)
    guard.press_key("ctrl+a")
    guard.sleep(0.08)
    guard.type_text(price_str)
    guard.sleep(0.1)
    guard.press_key("enter")
    guard.sleep(0.28)

    guard.click(cfg.point("ah_confirm_btn"),  before=0.12, after=0.45)


def listing_phase(cfg: Config, price: float, guard: AbortGuard) -> None:
    grid = build_slot_grid(cfg.point("ah_inv_top_left"), cfg.point("ah_inv_bottom_right"))

    img = grab_screen_pil()
    filled = [
        pos for i, pos in enumerate(grid)
        if i != SACRIFICE_SLOT_INDEX and not is_slot_empty(img, pos)
    ]

    if not filled:
        print("Keine zu listenden Items erkannt.")
        return

    price_str = f"{price:.2f}".replace(",", ".")
    print(f"Liste {len(filled)} Items fuer {price_str}.")

    for pos in filled:
        guard.check()
        list_one(guard, cfg, pos, price_str)
