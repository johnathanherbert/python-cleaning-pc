import flet as ft
from ui.app import CleanerApp

def main(page: ft.Page):
    page.title = "Sistema de Limpeza e Otimização"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 40

    page.add(CleanerApp(page))

if __name__ == "__main__":
    ft.app(target=main)