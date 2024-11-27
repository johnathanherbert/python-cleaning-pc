import flet as ft
from datetime import datetime

def create_memory_view(page: ft.Page, memory_manager):
    def update_memory_info():
        stats = memory_manager.get_memory_stats()
        memory_stats.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Memória RAM", size=24, weight="bold", color=ft.colors.BLUE_900),
                    ft.ProgressBar(
                        value=float(stats['percent'].strip('%')) / 100,
                        color=ft.colors.GREEN_400,
                        bgcolor=ft.colors.GREEN_100,
                        height=20,
                    ),
                    ft.Row([
                        ft.Text(f"Total: {stats['total']}", size=14, color=ft.colors.GREY_700),
                        ft.Text(f"Em uso: {stats['used']}", size=14, color=ft.colors.GREY_700),
                        ft.Text(f"Disponível: {stats['available']}", size=14, color=ft.colors.GREY_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Uso de Memória: {stats['percent']}", size=16, weight="bold", color=ft.colors.RED_400),
                ], spacing=10),
                padding=20,
                border=ft.border.all(1, ft.colors.BLUE_100),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(2, 2),
                )
            )
        ]
        page.update()

    def update_process_list():
        process_memory = memory_manager.get_memory_usage()
        process_list.controls = [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.MEMORY, color=ft.colors.BLUE),
                    title=ft.Text(proc['name'], size=14, weight="bold"),
                    subtitle=ft.Text(
                        f"Memória: {proc['memory_mb']:.2f} MB ({proc['memory_percent']:.2f}%)",
                        size=12
                    ),
                ),
                border=ft.border.all(1, ft.colors.BLUE_100),
                border_radius=8,
                margin=5,
            )
            for proc in process_memory
        ]
        page.update()

    memory_stats = ft.Column(spacing=10)
    process_list = ft.Column(
        spacing=5,
        scroll=ft.ScrollMode.ALWAYS,
        height=400,
    )

    # Botões de ação
    action_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "Atualizar",
                on_click=lambda _: (update_memory_info(), update_process_list()),
                icon=ft.icons.REFRESH,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.BLUE_500,
                    color=ft.colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            ),
            ft.ElevatedButton(
                "Limpar Memória",
                on_click=lambda _: (
                    page.show_snack_bar(ft.SnackBar(
                        content=ft.Text(memory_manager.clean_memory()),
                        action="OK"
                    )),
                    update_memory_info(),  # Atualiza as estatísticas
                    update_process_list()  # Atualiza a lista de processos
                ),
                icon=ft.icons.CLEANING_SERVICES,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.GREEN_500,
                    color=ft.colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            ),
            ft.ElevatedButton(
                "Otimizar Memória",
                on_click=lambda _: (
                    page.show_snack_bar(ft.SnackBar(
                        content=ft.Text(memory_manager.optimize_memory()),
                        action="OK"
                    )),
                    update_memory_info(),  # Atualiza as estatísticas
                    update_process_list()  # Atualiza a lista de processos
                ),
                icon=ft.icons.TUNE,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.ORANGE_500,
                    color=ft.colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )

    view = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Text("Visão Geral da Memória", size=28, weight="bold", color=ft.colors.BLUE_900),
                ft.Divider(height=1, color=ft.colors.BLUE_100),
                memory_stats,
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.BLUE_100),
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(2, 2),
            )
        ),
        action_buttons,  # Adiciona os botões de ação acima da tabela
        ft.Container(
            content=ft.Column([
                ft.Text("Processos com maior consumo de memória:", 
                       size=20, 
                       weight="bold", 
                       color=ft.colors.BLUE_900
                ),
                ft.Container(
                    content=process_list,
                    height=400,
                    border=ft.border.all(1, ft.colors.BLUE_100),
                    border_radius=10,
                    padding=10,
                ),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.colors.BLUE_100),
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(2, 2),
            )
        ),
    ], spacing=20)

    # Atualização inicial
    update_memory_info()
    update_process_list()

    return view