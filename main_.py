# Main py
# Description: The main panel framework of ClassTools
# LunareZ @A_xie_A
# => Copyright Apathy 3.0 <=
import flet as ft
from time import sleep
from Base import Base
from modmanager import ModManager


# Main Function
def main(page: ft.Page):
    ########## Windows profile ##########
    page.title = "ClassTools"

    page.window.title_bar_hidden = True
    page.window.start_dragging()
    page.window.resizable = True

    sidebar = ft.Ref[ft.Container]
    sidebar_clicked = ft.Ref[ft.Container]
    SIDEBAR_COLLAPSED_WIDTH = 75
    SIDEBAR_EXPANDED_WIDTH = 190
    MAIN_PANEL_WIDTH = 1440
    if sidebar:
        WINDOW_WIDTH = MAIN_PANEL_WIDTH + 190
    else:
        WINDOW_WIDTH = MAIN_PANEL_WIDTH + 75
    WINDOW_HEIGHT = 800

    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT

    ########## Windows Style ##########
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.bgcolor = ft.Colors.with_opacity(1, "GREY_700")

    ########## Title Bar ##########
    def minimize(_):
        page.window.minimized = True

    def maximize(e):
        page.window.maximized = not page.window.maximized
        e.control.icon = ft.Icons.CHECK_BOX_OUTLINE_BLANK if page.window.maximized else ft.Icons.CROP_SQUARE
        e.control.update()

    async def close_app(_):
        for mod in mod_manager.mods:
            mod.destroy()
        await page.window.close()
        page.update()

    def button_style(normal_bg, hover_bg, icon_color):
        return ft.ButtonStyle(
            bgcolor=normal_bg,
            color=icon_color,
            overlay_color=hover_bg,
            shape=ft.RoundedRectangleBorder(radius=4),
            padding=ft.padding.all(4)
        )

    TRANSPARENT = ft.Colors.TRANSPARENT
    HOVER_GRAY = ft.Colors.with_opacity(0.1, ft.Colors.GREY_200)
    HOVER_RED = ft.Colors.with_opacity(0.9, ft.Colors.RED_500)
    ICON_GRAY = ft.Colors.with_opacity(0.8, ft.Colors.GREY_400)
    ICON_SIZE = 17

    title_bar = ft.Row(
        controls=[
            ft.WindowDragArea(
                content=ft.Container(
                    expand=True,
                    height=40,
                    bgcolor=ft.Colors.with_opacity(1, "GREY_700"),
                ),
                expand=True,
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.MINIMIZE,
                            icon_size=ICON_SIZE,
                            on_click=minimize,
                            style=button_style(TRANSPARENT, HOVER_GRAY, ICON_GRAY)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CROP_SQUARE,
                            icon_size=ICON_SIZE,
                            on_click=maximize,
                            style=button_style(TRANSPARENT, HOVER_GRAY, ICON_GRAY),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=ICON_SIZE,
                            on_click=close_app,
                            style=button_style(TRANSPARENT, HOVER_RED, ICON_GRAY)
                        )
                    ],
                    spacing=0,
                    height=40,
                ),
                padding=ft.Padding.only(right=8),
            ),
        ],
        height=40,
        spacing=0,
    )

    ########## Side Bar ##########
    mod_manager = ModManager(page)

    sidebar_content = mod_manager.create_sidebar_content(SIDEBAR_EXPANDED_WIDTH)
    sidebar_clicked = False

    def update_mod_items_visibility(is_expanded):
        for mod_item in sidebar_content.controls:
            if hasattr(mod_item, "update_name_visibility"):
                mod_item.update_name_visibility(is_expanded)

    def handle_sidebar_click(_):
        nonlocal sidebar_clicked
        sidebar_clicked = not sidebar_clicked
        sidebar_container.width = SIDEBAR_EXPANDED_WIDTH if sidebar_clicked else SIDEBAR_COLLAPSED_WIDTH
        update_mod_items_visibility(sidebar_clicked)
        sidebar_container.update()

    def handle_sidebar_hover(e):
        nonlocal sidebar_clicked
        is_hover = e.data == "true" or e.data is True
        sleep(0.2)
        if not sidebar_clicked:
            sidebar_container.width = SIDEBAR_EXPANDED_WIDTH if is_hover else SIDEBAR_COLLAPSED_WIDTH
            update_mod_items_visibility(is_hover)
            sidebar_container.update()

    sidebar_container = ft.Container(
        content=sidebar_content,
        width=SIDEBAR_COLLAPSED_WIDTH,
        height=None,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=ft.border_radius.only(top_right=8, bottom_right=8),
        on_click=handle_sidebar_click,
        on_hover=handle_sidebar_hover,
        ink=False
    )

    ########## Root Panel ##########
    main_content = ft.Container(
        content=ft.Text(
            value=f"ClassTools 主界面\n"
                  f"已加载Mod数量: {len(mod_manager.mods)}\n"
                  f"点击侧边栏Mod图标查看功能",
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.GREY_700,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=page.bgcolor,
        margin=ft.margin.all(10),
        padding = ft.padding.all(10)
    )

    def on_mod_click_custom(mod: Base):
        nonlocal main_content
        main_content.content = mod.build(page)
        main_content.update()

    mod_manager.on_mod_click = on_mod_click_custom

    right_column = ft.Column(
        controls=[
            title_bar,
            main_content
        ],
        spacing=0,
        expand=True
    )

    root = ft.Row(
        controls=[
            sidebar_container,
            right_column
        ],
        spacing=0,
        expand=True
    )

    page.add(root)

if __name__ == "__main__":
    ft.app(target=main)
