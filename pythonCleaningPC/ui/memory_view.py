import flet as ft
from datetime import datetime

def create_memory_view(page: ft.Page, memory_manager):
    def update_memory_info():
        stats = memory_manager.get_memory_stats()
        memory_stats.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Memória RAM", size=20, weight="bold"),
                    ft.ProgressBar(
                        value=float(stats['percent'].strip('%')) / 100,
                        color="blue",
                        bgcolor=ft.colors.BLUE_100,
                    ),
                    ft.Row([
                        ft.Text(f"Total: {stats['total']}", size=14),
                        ft.Text(f"Em uso: {stats['used']}", size=14),
                        ft.Text(f"Disponível: {stats['available']}", size=14),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ]),
                padding=10,
                border=ft.border.all(1, ft.colors.BLUE_200),
                border_radius=10,
            )
        ]
        page.update()

    def update_process_list():
        processes = memory_manager.get_memory_usage()
        process_list.controls = [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Processo")),
                    ft.DataColumn(ft.Text("Uso de Memória (MB)"), numeric=True),
                    ft.DataColumn(ft.Text("Porcentagem"), numeric=True),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(p['name'])),
                            ft.DataCell(ft.Text(f"{p['memory_mb']:.1f}")),
                            ft.DataCell(ft.Text(f"{p['memory_percent']:.1f}%")),
                        ],
                    ) for p in processes[:20]  # Mostrar top 20 processos
                ],
            )
        ]
        page.update()

    def optimize_memory_click(_):
        cleared = memory_manager.optimize_memory()
        update_memory_info()
        update_process_list()
        
        # Criando o Snackbar
        snack = ft.SnackBar(
            content=ft.Text(f"Memória otimizada! {cleared} processos afetados."),
            action="OK"
        )
        # Usando o novo método page.open()
        page.open = snack
        page.update()

    memory_stats = ft.Column(spacing=10)
    process_list = ft.Column(spacing=10)
    
    view = ft.Column([
        ft.Row([
            ft.ElevatedButton(
                "Otimizar Memória",
                on_click=optimize_memory_click,
                icon=ft.icons.MEMORY
            ),
            ft.ElevatedButton(
                "Atualizar",
                on_click=lambda _: (update_memory_info(), update_process_list()),
                icon=ft.icons.REFRESH
            ),
        ]),
        memory_stats,
        ft.Text("Processos com maior consumo de memória:", size=16, weight="bold"),
        process_list,
    ], spacing=20)

    # Atualização inicial
    update_memory_info()
    update_process_list()

    return view