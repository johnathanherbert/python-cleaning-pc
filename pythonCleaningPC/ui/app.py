import flet as ft
import asyncio
from core.analyzer import SystemAnalyzer
from core.cleaner import SystemCleaner
from core.memory_manager import MemoryManager
from ui.components import create_result_card, show_details_dialog, create_whitelist_dialog
from ui.memory_view import create_memory_view

def CleanerApp(page: ft.Page):
    # Configurações da página
    page.theme_mode = ft.ThemeMode.LIGHT  # Força o modo claro
    page.bgcolor = ft.colors.WHITE  # Define o fundo branco
    page.window.bgcolor = ft.colors.WHITE  # Define o fundo da janela
    page.update()

    analyzer = SystemAnalyzer()
    cleaner = SystemCleaner()
    memory_manager = MemoryManager()
    
    # Estilo consistente para textos
    title_style = {"size": 20, "weight": "bold", "color": ft.colors.BLUE_900}
    subtitle_style = {"size": 16, "weight": "bold", "color": ft.colors.BLUE_700}
    text_style = {"size": 14, "color": ft.colors.BLACK}
    
    status = ft.Text(
        "Aguardando ação...", 
        **subtitle_style,
    )
    
    progress_bar = ft.ProgressBar(
        width=300, 
        value=0.0, 
        color=ft.colors.BLUE_400,
        bgcolor=ft.colors.BLUE_50,
    )
    
    def handle_analyze_click(e):
        asyncio.run(start_analysis(page))
        
    def handle_clean_click(e):
        asyncio.run(start_cleaning(page))
    
    def handle_whitelist_click(e):
        dlg = create_whitelist_dialog(page, analyzer.whitelist_manager, analyzer)
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    # Estilo comum para botões
    button_style = {
        "style": ft.ButtonStyle(
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        )
    }
    
    analyze_button = ft.ElevatedButton(
        "Analisar Sistema",
        on_click=handle_analyze_click,
        icon=ft.icons.SEARCH,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        )
    )
    
    start_button = ft.ElevatedButton(
        "Iniciar Limpeza",
        on_click=handle_clean_click,
        icon=ft.icons.CLEANING_SERVICES,
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.GREEN_500,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        )
    )
    
    whitelist_button = ft.ElevatedButton(
        "Gerenciar Whitelist",
        on_click=handle_whitelist_click,
        icon=ft.icons.LIST,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.ORANGE_500,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
        )
    )

    async def start_analysis(page: ft.Page):
        analyze_button.disabled = True
        result_cards.controls.clear()
        page.update()

        tasks = [
            ("Analisando arquivos temporários", analyzer.analyze_temp_files, ft.icons.FILE_PRESENT, analyzer.temp_files_details),
            ("Analisando processos", analyzer.analyze_unnecessary_processes, ft.icons.MEMORY, analyzer.unnecessary_processes_details),
            ("Analisando cache", analyzer.analyze_cache, ft.icons.STORAGE, analyzer.cache_details)
        ]

        total_tasks = len(tasks)
        for i, (task_name, task_func, task_icon, task_details) in enumerate(tasks):
            status.value = task_name
            page.update()

            result = task_func()
            card = create_result_card(
                task_name=task_name,
                result=result,
                task_icon=task_icon,
                task_details=task_details,
                on_details_click=lambda e, details=task_details, title=task_name: show_details_dialog(
                    page=page,
                    details=details,
                    title=title,
                    analyzer=analyzer
                )
            )
            result_cards.controls.append(card)

            # Atualiza a barra de progresso após cada tarefa
            progress_bar.value = (i + 1) / total_tasks
            page.update()

        status.value = "Análise concluída. Pronto para limpeza!"
        progress_bar.value = 1.0
        analyze_button.disabled = False
        start_button.disabled = False
        page.update()

    async def start_cleaning(page: ft.Page):
        try:
            start_button.disabled = True
            result_cards.controls.clear()
            page.update()

            tasks = [
                ("Limpando arquivos temporários", cleaner.clean_temp_files, ft.icons.FILE_PRESENT),
                ("Limpando cache", cleaner.clean_cache, ft.icons.STORAGE),
                ("Otimizando cache", cleaner.optimize_cache, ft.icons.STORAGE)
            ]

            for i, (task_name, task_func, task_icon) in enumerate(tasks):
                try:
                    status.value = task_name
                    progress_bar.value = (i + 1) / len(tasks)
                    page.update()

                    result = task_func()
                    card = create_result_card(
                        task_name=task_name,
                        result=result,
                        task_icon=task_icon
                    )
                    result_cards.controls.append(card)
                    page.update()
                except Exception as e:
                    print(f"Erro durante a tarefa {task_name}: {e}")
                    status.value = f"Erro durante {task_name}"
                    page.update()

            status.value = "Limpeza concluída!"
            progress_bar.value = 1.0
        except Exception as e:
            print(f"Erro durante a limpeza: {e}")
            status.value = "Erro durante a limpeza"
        finally:
            start_button.disabled = False
            page.update()

    result_cards = ft.Row(
        spacing=20, 
        alignment=ft.MainAxisAlignment.CENTER,
        wrap=True,  # Permite que os cards quebrem linha quando necessário
    )
    
    # Criar tabs para diferentes funcionalidades
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Limpeza",
                icon=ft.icons.CLEANING_SERVICES,
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Limpeza do Sistema", **title_style),
                            ft.Divider(height=1, color=ft.colors.BLUE_100),
                            status,
                            progress_bar,
                            ft.Row(
                                [analyze_button, start_button, whitelist_button], 
                                spacing=10, 
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                        ], 
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30,
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
                ft.Container(
                    content=result_cards,
                    padding=20,
                ),
            ], 
            spacing=30,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )),
        ft.Tab(
            text="Memória",
            icon=ft.icons.MEMORY,
            content=create_memory_view(page, memory_manager)
        ),
    ])
    
    return ft.Container(
        content=tabs,
        padding=20,
        bgcolor=ft.colors.WHITE,
    )