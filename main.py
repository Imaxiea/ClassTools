# Main py
# Description: The main panel framework of ClassTools
# LunareZ @A_xie_A
# => Copyright Apathy 3.0 <=
import flet as ft
import json
import os
import uuid
import threading
from importlib.util import spec_from_file_location, module_from_spec
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ===== Configuration ===== #
CONFIG_PATH = 'config.json'
MODS_PATH = 'mods'
ANIM_DURATION = 260
THEME = {
    "bg": "#1e1e1e",
    "panel": "#252525",
    "hover": "#333333",
    "text": "#e0e0e0",
    "subtext": "#999999",
    "accent": "#007acc",
    "border": "#3a3a3a"
}
# ======================== #

# ===== Tool Functions ===== #
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mods": []}

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
# ========================== #

# ==== Mods Loading ===== #
def scan_mods():
    mods = {}
    # Open Mod Folder
    if not os.path.exists(MODS_PATH):
        os.makedirs(MODS_PATH)

    # Load Mods
    for item in os.listdir(MODS_PATH):
        d = os.path.join(MODS_PATH, item)
        if not os.path.isdir(d):
            continue
        mod_py = os.path.join(d, "mod.py")
        if not os.path.exists(mod_py):
            continue
        try:
            spec = spec_from_file_location(f"mod_{uuid.uuid4()}", mod_py)
            # None Value Judgment
            if spec is None:
                print(f"Loading Failed: {item} | Cannot get mod spec")
                continue
            if spec.loader is None:
                print(f"Loading Failed: {item} | Cannot get mod loader")
                continue
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            mod = module.create_mod()
            mods[mod.mod_id] = mod
        except Exception as e:
            print(f"loading Failed: {item} | {e}")
    return mods
# ======================= #
