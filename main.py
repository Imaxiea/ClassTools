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

from flet import Page
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

# ===== Folder Listener ===== #
class ModWatcher(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        self._debounce_timer = None

    def on_any_event(self, event):
        if event.is_directory:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = ft.Timer(
                0.3,
                lambda _: self._do_reload(),
                repeat=False
            )
            self._debounce_timer.start()

    def _do_reload(self):
        self._debounce_timer = None
        self.app.hot_reload()

# =========================== #

# ===== Mod Tab ===== #
class ModItem(ft.Container):
    def __init__(self, mod, app):
        super().__init__()
        self.mod = mod
        self.app = app
        self.width = 52
        self.bgcolor = ft.colors.TRANSPARENT
        self.border_radius = 8
        self.padding = ft.padding.symmetric(10, 8)
        self.animate = ft.Animation(ANIM_DURATION, ft.AnimationCurve.EASE_OUT)
        self.on_click = lambda _: self.app.open_mod(mod.mod_id)
        self.on_secondary_tap = self.show_menu
        self.on_hover = self._hover

        self.icon = ft.Icon(mod.icon, size=22, color=THEME["subtext"])
        self.title = ft.Text(
            mod.name, size=13, color=THEME["text"],
            width=0, opacity=0, animate_opacity=ANIM_DURATION
        )

        self.content = ft.Row([self.icon, self.title], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _hover(self, e):
        if e.data == "true":
            self.width = 150
            self.bgcolor = THEME["hover"]
            self.title.opacity = 1
            self.title.width = 80
        else:
            self.width = 52
            self.bgcolor = ft.colors.TRANSPARENT
            self.title.opacity = 0
            self.title.width = 0
        self.update()

    def show_menu(self, _):
        total = len(self.app.config["mods"])
        disable_del = total <= 1

        menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CLOSE, color=ft.colors.RED, size=18),
                        ft.Text("Delete", color=ft.colors.WHITE, size=14),
                    ], spacing=8),
                    on_click=lambda _: self.app.confirm_del(self.mod.mod_id),
                    disabled=disable_del
                ),
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT, color=ft.colors.RED, size=18),
                        ft.Text("Rename", size=14),
                    ], spacing=8),
                    on_click=lambda _: self.app.rename_mod(self.mod.mod_id)
                ),
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REFRESH, color=ft.colors.RED, size=18),
                        ft.Text("Reload", size=14),
                    ], spacing=8),
                    on_click=lambda _: self.app.reload_mod(self.mod.mod_id)
                ),
            ]
        )

        if isinstance(self.content, ft.Row) and self.content.controls:
            assert isinstance(menu, ft.PopupMenuButton)
            self.content.controls[-1].visible = True
            self.content.controls[-1].update()
# =================== #

# ===== Main Program ===== #
class ClassTools:
    def __init__(self, page: Page):
        self.page = page
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = THEME["bg"]
        self.page.window_title_bar_hidden = True
        self.page.window_frameless = True
        self.page.window_width = 1080
        self.page.window_height = 720

        self.mods = scan_mods()
        self.config = load_config()
        self.current_id = None

        # Left & Right Board
        self.mod_list = ft.Column(spacing=2, scroll=ft.ScrollMode.ALWAYS)
        self.left_bar = ft.Container(
            content=self.mod_list,
            width=52, bgcolor=THEME["panel"],
            border=ft.Border(right=ft.BorderSide(1, THEME["border"])),
            animate=ft.Animation(ANIM_DURATION)
        )
        self.placeholder = ft.Icon(ft.Icons.CHECK_ROUNDED, size=70, color="#444444")
        self.content_panel = ft.Container(
            content=self.placeholder,
            expand=True, alignment=ft.Alignment.CENTER, bgcolor=THEME["bg"]
        )

        # Root
        self.page.add(
            ft.WindowDragArea(
                ft.Row([self.left_bar, self.content_panel], expand=True, spacing=0),
                maximizable=False
            )
        )

        self.refresh_list()
        self.start_watcher()

    # Refresh Function
    def refresh_list(self):
        self.mod_list.controls.clear()
        for mid in self.config["mods"]:
            if mid in self.mods:
                self.mod_list.controls.append(ModItem(self.mods[mid], self))
        self.mod_list.update()

    # Mod Opener Tool
    def open_mod(self, mid):
        self.current_id = mid
        ui = self.mods[mid].build_ui(self.page)
        self.content_panel.content = ui
        self.content_panel.update()

    # Hot Reload Function
    def hot_reload(self):
        new_mods = scan_mods()
        self.mods = new_mods
        ft.Timer(0, self.refresh_list, repeat=False).start()

    # Mod Reloader
    def reload_mod(self, mid):
        self.hot_reload()
        if self.current_id == mid:
            self.open_mod(mid)

    # Mod Renamer
    def rename_mod(self, mid):
        mod = self.mods[mid]

        def close_dlg(_):
            self.page.dialog = None
            self.page.update()

        def ok(_):
            val = tf.value.strip()
            if val:
                mod.name = val
                self.refresh_list()
            close_dlg(_)

        tf = ft.TextField(
            label='New Name',
            value=mod.name,
            bgcolor=THEME['panel'],
            color=THEME['text']
        )

        dlg = ft.AlertDialog(
            title=ft.Text('Rename MOD', color=THEME['text']),
            content=tf,
            actions=[
                ft.Button(
                    'Cancel',
                    on_click=close_dlg,
                    color=THEME['text'],
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.TRANSPARENT,
                        elevation=0
                    )
                ),
                ft.Button(
                    'Confirm',
                    on_click=ok,
                    color=THEME['text'],
                    style=ft.ButtonStyle(
                        bgcolor=THEME['accent'],
                        elevation=2
                    )
                )
            ],
            bgcolor=THEME['panel']
        )

        self.page.dialog = dlg
        self.page.update()

    # Mod Deleter
    def confirm_del(self, mid):
        def close_dlg(_):
            self.page.dialog = None
            self.page.update()

        def ok(_):
            self.config['mods'].remove(mid)
            save_config(self.config)
            if self.current_id == mid:
                self.content_panel.content = self.placeholder
                self.current_id = None
                self.content_panel.update()
            self.refresh_list()
            close_dlg(_)

        dlg = ft.AlertDialog(
            title=ft.Text('Confirm Delete', color=THEME['text']),
            content=ft.Text('This MOD will be deleted from MOD Tab, Continue?', color=THEME['text']),
            actions=[
                ft.Button(
                    'Cancel',
                    on_click=close_dlg,
                    color=THEME["text"]
                ),
                ft.Button(
                    'Confirm',
                    on_click=ok,
                    color=ft.colors.RED
                )
            ],
            bgcolor=THEME["panel"]
        )

        self.page.dialog = dlg
        self.page.update()

    def start_watcher(self):
        handler = ModWatcher(self)
        observer = Observer()
        observer.schedule(handler, MODS_PATH, recursive=True)
        observer.start()

def main(page: ft.Page):
    ClassTools(page)

if __name__ == "__main__":
    ft.app(target=main)
