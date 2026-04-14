# mods/ExampleMod/main.py
# Description: Example Mod
# @DouBao
from Base import Base
import flet as ft


class ExampleMod(Base):
    @property
    def id(self) -> str:
        return "example_mod"

    @property
    def name(self) -> str:
        return "Example Mod - Long name Display Test"

    @property
    def icon(self) -> str:
        return "STAR_BORDER"

    # 必须实现的抽象方法
    def build(self, page: ft.Page) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"欢迎使用 {self.name}", size=24, color=ft.Colors.WHITE),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.Text(
                        "这是示例Mod的功能面板\n"
                        "1. 侧边栏点击图标可打开此面板\n"
                        "2. 侧边栏展开时显示完整名称（超长会自动截断）\n"
                        "3. 收起时仅显示图标",
                        size=16,
                        color=ft.Colors.WHITE70,
                    )
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )

    def init(self):
        print(f"[{self.name}] 已初始化")

    def destroy(self):

        print(f"[{self.name}] 已销毁")


if __name__ == "__main__":
    def test(page: ft.Page):
        mod = ExampleMod()
        page.add(mod.build(page))

    ft.app(target=test)
