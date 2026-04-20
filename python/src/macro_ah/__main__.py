"""CLI-Entry: Kalibrierung -> Preis-Dialog -> Hotkey-Warten -> Split + Listing."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import keyboard
import pyautogui

from .automation import ask_price, calibrate_dialog, listing_phase, open_ah, split_phase
from .config import load_config, save_config
from .safety import AbortGuard, Aborted


DEFAULT_CONFIG_PATH = Path.cwd() / "config.json"


def main() -> None:
    parser = argparse.ArgumentParser(prog="macro-ah", description="Halb-automatisches /ah-Listing fuer HugoSMP.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Pfad zur config.json")
    parser.add_argument("--calibrate", action="store_true", help="Kalibrierung erzwingen")
    args = parser.parse_args()

    pyautogui.PAUSE = 0.03
    pyautogui.FAILSAFE = True

    cfg = load_config(args.config)

    if args.calibrate or not cfg.is_calibrated():
        print("Starte Kalibrierung.")
        new_cfg = calibrate_dialog()
        if new_cfg is None:
            print("Kalibrierung abgebrochen.")
            return
        cfg = new_cfg
        save_config(cfg, args.config)

    price = ask_price()
    if price is None:
        return

    print()
    print("Bereit.")
    print("Wechsle zu Minecraft.")
    print("Bedingungen: Inventar leer ausser EINEM Stack; Slot 1 (oben-links) muss frei sein.")
    print("Start: Strg+Leertaste. Abbruch: Esc oder Mausbewegung.")
    print()

    keyboard.wait("ctrl+space")
    time.sleep(0.6)

    try:
        guard = AbortGuard()
        split_phase(cfg, guard)
        open_ah(guard)
        guard.reset_baseline()
        listing_phase(cfg, price, guard)
        print("Fertig.")
    except Aborted as e:
        print(f"Abgebrochen: {e}")
    except Exception as e:
        print(f"Fehler: {e}")


if __name__ == "__main__":
    main()
