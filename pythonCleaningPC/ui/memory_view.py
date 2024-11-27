import flet as ft
from datetime import datetime
import asyncio

def create_memory_view(page: ft.Page, memory_manager):
    # Estilo consistente para textos
    title_style = {"size": 22, "weight": "bold", "color": ft.colors.BLUE_800}
    subtitle_style = {"size": 18, "weight": "bold", "color": ft.colors.GREY_600}
    text_style = {"size": 16, "color": ft.colors.GREY_700}

    # Inicializa os controles
    memory_stats = ft.Column(controls=[], spacing=10)
    process_list = ft.Column(controls=[], spacing=5)

    # Estilo comum para botões
    button_style = ft.ButtonStyle(
        color=ft.colors.WHITE,
        bgcolor=ft.colors.GREEN_400,
        shape=ft.RoundedRectangleBorder(radius=8),
    )

    def handle_clean_memory(e):
        async def do_clean():
            try:
                status_text.value = "Limpando memória RAM..."
                page.update()
                
                result = await asyncio.to_thread(memory_manager.clean_memory)
                
                # Atualiza as informações após a limpeza
                update_memory_info()
                update_process_list()
                
                page.show_snack_bar(ft.SnackBar(
                    content=ft.Text(result),
                    action="OK"
                ))
                status_text.value = "Memória RAM limpa com sucesso!"
            except Exception as ex:
                status_text.value = f"Erro ao limpar memória: {str(ex)}"
            finally:
                page.update()
        
        asyncio.run(do_clean())

    def handle_optimize_memory(e):
        async def do_optimize():
            try:
                status_text.value = "Otimizando memória RAM..."
                page.update()
                
                result = await asyncio.to_thread(memory_manager.optimize_memory)
                
                # Atualiza as informações após a otimização
                update_memory_info()
                update_process_list()
                
                page.show_snack_bar(ft.SnackBar(
                    content=ft.Text(result),
                    action="OK"
                ))
                status_text.value = "Memória RAM otimizada com sucesso!"
            except Exception as ex:
                status_text.value = f"Erro ao otimizar memória: {str(ex)}"
            finally:
                page.update()
        
        asyncio.run(do_optimize())

    # Botões de ação
    clean_button = ft.ElevatedButton(
        "Limpar Memória",
        icon=ft.icons.CLEANING_SERVICES,
        on_click=handle_clean_memory,  # Usando a função handler
        style=button_style
    )

    optimize_button = ft.ElevatedButton(
        "Otimizar Memória",
        icon=ft.icons.MEMORY,
        on_click=handle_optimize_memory,  # Usando a função handler
        style=button_style
    )

    # Status text
    status_text = ft.Text(
        "Aguardando ação...",
        color=ft.colors.GREY_700,
        size=14,
    )

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
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=12,
                bgcolor=ft.colors.GREY_50,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
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
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=8,
                margin=5,
            )
            for proc in process_memory[:10]  # Limita a 10 processos
        ]
        page.update()

    # Botão de atualizar
    refresh_button = ft.ElevatedButton(
        "Atualizar",
        icon=ft.icons.REFRESH,
        on_click=lambda _: (update_memory_info(), update_process_list()),
        style=button_style,
    )

    view = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Visão Geral da Memória", **title_style),
                    ft.Row([clean_button, optimize_button], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=ft.colors.BLUE_100),
                status_text,
                memory_stats,
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=12,
            bgcolor=ft.colors.GREY_50,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(2, 2),
            )
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Processos com maior consumo de memória:", **title_style),
                ft.Divider(height=1, color=ft.colors.BLUE_100),
                ft.Container(
                    content=ft.Column(
                        controls=[process_list],
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    height=400,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    padding=10,
                    bgcolor=ft.colors.WHITE,
                ),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(2, 2),
            )
        ),
    ], spacing=30)

    # Atualização inicial
    update_memory_info()
    update_process_list()

    return view