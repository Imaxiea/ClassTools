# mods/ExampleMod/main.py
# Description: Rolling Mod
# @DouBao
from Base import Base
import flet as ft


class Rolling(Base):
    @property
    def id(self) -> str:
        return 'rolling'

    @property
    def name(self) -> str:
        return 'Rolling'

    @property
    def icon(self) -> str:
        return 'TOLL'

    def init(self):
        print(f'[{self.name}] has already loaded.')

    def destroy(self):
        print(f"[{self.name}] has already destroyed.")

    def build(self, page: ft.Page) -> ft.Control:
        return ft.Container(

        )

if __name__ == "__main__":
    def roll(page: ft.Page):
        mod = Rolling()
        page.add(mod.build(page))

    ft.app(target=roll)
