# Mod Manager py
# Description: Load mods and manage the display of mods
# LunareZ @A_xie_A
# => Copyright Apathy 3.0 <=
import os
import importlib.util
from Base import Base
from flet import Page, Icon, Icons, Colors, Text, TextAlign, Container, Padding, Animation, Row, MainAxisAlignment, \
    Column, AnimationCurve, IconData, Alignment, padding
from typing import List, Optional


# Mod Manager Class
class ModManager:
    def __init__(self, page: Page):
        self.page = page
        self.mods: List[Base] = []
        self.load_mods()

    def load_mods(self):
        mods_dir = 'mods'
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
            return

        for mod_name in os.listdir(mods_dir):
            mod_path = os.path.join(mods_dir, mod_name, 'main.py')
            if not os.path.exists(mod_path):
                continue

            spec: Optional[importlib.util.ModuleSpec] = importlib.util.spec_from_file_location(
                f'mods.{mod_name}.main', mod_path
            )
            if spec is None:
                print(f'警告：无法加载Mod {mod_name}，模块规范创建失败')
                continue

            mod_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod_module)

            for attr in dir(mod_module):
                cls = getattr(mod_module, attr)
                if isinstance(cls, type) and issubclass(cls, Base) and cls is not Base:
                    mod_instance = cls()
                    mod_instance.init()  # 执行Mod初始化
                    self.mods.append(mod_instance)
                    break

    def create_mod_sidebar_item(self, mod: Base, sidebar_expanded_width: int) -> Container:
        is_selected = False

        def icon_data(icon_str: str) -> IconData:
            icon_str = icon_str.strip().upper()
            try:
                return getattr(Icons, icon_str)
            except AttributeError:
                print(f'警告：Mod {mod.name} 的图标 {icon_str} 不存在，使用默认图标')
                return Icons.QUESTION_MARK

        def on_mod_click(_):
            nonlocal is_selected

            is_selected = not is_selected
            icon_container.bgcolor = Colors.with_opacity(0.2,Colors.WHITE) if is_selected else Colors.TRANSPARENT
            mod_item.update()

            sidebar_column = self.page.controls[0].controls[0].content
            for item in sidebar_column.controls:
                if item != mod_item:
                    item_icon_container = item.content.controls[0]
                    item_mod_icon = item_icon_container.content
                    item_icon_container.bgcolor = Colors.TRANSPARENT
                    item_mod_icon.filled = False
                    item_icon_container.update()
                    item_mod_icon.update()
            if not is_selected:
                is_selected = True
                icon_container.bgcolor = Colors.with_opacity(0.2, Colors.WHITE)
                mod_icon.filled = True
            icon_container.update()
            mod_icon.update()

            root_row = self.page.controls[0]
            right_column = root_row.controls[1]
            main_content = right_column.controls[1]
            main_content.content = mod.build(self.page)
            main_content.update()

        mod_icon = Icon(
            icon=icon_data(mod.icon),
            color=Colors.WHITE,
            size=22,
        )

        icon_container = Container(
            content=mod_icon,
            border_radius=6,
            alignment=Alignment.CENTER,
            padding=padding.all(12),
            bgcolor=Colors.with_opacity(0.2, Colors.WHITE) if is_selected else Colors.TRANSPARENT,
            animate=Animation(
                duration=300,
                curve=AnimationCurve.EASE_IN_OUT
            ),
        )

        mod_name_text = Text(
            value=get_truncated_name(mod.name, sidebar_expanded_width - 40),
            color=Colors.WHITE,
            size=14,
            text_align=TextAlign.LEFT,
        )

        mod_item = Container(
            content=Row(
                controls=[
                    icon_container,
                    Container(
                        content=mod_name_text,
                        expand=True,
                        padding=Padding(left=10),
                        opacity=0,
                        animate_opacity=Animation(300, AnimationCurve.EASE_IN_OUT)
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                spacing=0,
            ),
            height=50,
            padding=Padding(left=15, right=15),
            on_click=on_mod_click,
            border_radius=4,
            data=mod.id,
        )

        mod_item.update_name_visibility = lambda is_expanded: self.update_mod_item_visibility(
            mod_item, is_expanded, sidebar_expanded_width
        )

        return mod_item

    @staticmethod
    def update_mod_item_visibility(mod_item: Container, is_expanded: bool, max_width: int):

        name_container = mod_item.content.controls[1]
        if is_expanded:
            mod_name_text = name_container.content
            mod_name_text.value = get_truncated_name(mod_name_text.value.split("....")[0], max_width - 40)
            name_container.opacity = 1
        else:
            name_container.opacity = 0
        mod_item.update()

    def on_mod_click(self, mod: Base):
        main_content = self.page.controls[0].controls[1].controls[1]
        main_content.content = mod.build(self.page)
        main_content.update()

    def create_sidebar_content(self, sidebar_expanded_width: int) -> Column:
        mod_items = [
            self.create_mod_sidebar_item(mod, sidebar_expanded_width)
            for mod in self.mods
        ]

        sidebar_content = Column(
            controls=mod_items,
            spacing=5,
            alignment=MainAxisAlignment.START,
            expand=True,
        )
        return sidebar_content

    def update_all_mod_items(self, is_expanded: bool, sidebar_expanded_width: int):
        for mod_item in self.create_sidebar_content(sidebar_expanded_width).controls:
            if hasattr(mod_item, 'update_name_visibility'):
                mod_item.update_name_visibility(is_expanded)

def get_truncated_name(name: str, max_width: int) -> str:
    max_chars = max_width // 8 - 1
    if len(name) > max_chars:
        return name[:max_chars] + '....'
    return name
