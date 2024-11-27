import flet as ft
import asyncio
from core.analyzer import SystemAnalyzer
from core.cleaner import SystemCleaner
from core.memory_manager import MemoryManager
from ui.components import create_result_card, show_details_dialog, create_whitelist_dialog
from ui.memory_view import create_memory_view

def CleanerApp(page: ft.Page):
    # Configurações da página
    page.update()

    analyzer = SystemAnalyzer()
    cleaner = SystemCleaner()
    memory_manager = MemoryManager()
    
    # Estilo consistente para textos
    title_style = {"size": 22, "weight": "bold", "color": ft.colors.BLUE_800}
    subtitle_style = {"size": 18, "weight": "bold", "color": ft.colors.GREY_600}
    text_style = {"size": 16, "color": ft.colors.GREY_700}
    
    status = ft.Text(
        "Aguardando ação...", 
        **subtitle_style,
    )
    
    progress_bar = ft.ProgressBar(
        width=300, 
        value=0.0, 
        color=ft.colors.GREEN_400,
        bgcolor=ft.colors.GREEN_100,
        visible=False  # Inicialmente invisível
    )
    
    progress_ring = ft.ProgressRing(
        color=ft.colors.GREEN_400,
        width=50,
        height=50,
        visible=False  # Inicialmente invisível
    )
    
    async def handle_analyze_click(e):
        asyncio.create_task(analyze_system(e))

    async def analyze_system(e):
        # Mostra os indicadores de progresso
        progress_ring.visible = True
        progress_bar.visible = True
        status.value = "Analisando sistema..."
        page.update()

        try:
            # Ativa os loadings nos cards
            for card in result_cards.controls:
                card.content.controls[2].controls[0].visible = True
            page.update()

            # Análise dos arquivos temporários
            progress_bar.value = 0.3
            page.update()
            temp_files = await asyncio.to_thread(analyzer.analyze_temp_files)
            result_cards.controls[0].content.controls[2].controls[1].value = f"{temp_files} arquivos"
            result_cards.controls[0].content.controls[2].controls[0].visible = False
            page.update()
            
            # Análise dos processos
            progress_bar.value = 0.6
            page.update()
            processes = await asyncio.to_thread(analyzer.analyze_unnecessary_processes)
            result_cards.controls[1].content.controls[2].controls[1].value = f"{processes} processos"
            result_cards.controls[1].content.controls[2].controls[0].visible = False
            page.update()
            
            # Análise do cache
            progress_bar.value = 0.9
            page.update()
            cache = await asyncio.to_thread(analyzer.analyze_cache)
            result_cards.controls[2].content.controls[2].controls[1].value = f"{cache} MB"
            result_cards.controls[2].content.controls[2].controls[0].visible = False
            page.update()
            
            # Finaliza a análise
            progress_bar.value = 1.0
            status.value = "Análise concluída!"
            page.update()
            
        except Exception as e:
            status.value = f"Erro durante a análise: {str(e)}"
        finally:
            progress_ring.visible = False
            progress_bar.visible = False
            progress_bar.value = 0
            page.update()
    
    async def start_cleaning(page):
        try:
            # Mostra os indicadores de progresso
            progress_ring.visible = True
            progress_bar.visible = True
            status.value = "Iniciando limpeza do sistema..."
            page.update()

            # Limpa arquivos temporários
            progress_bar.value = 0.3
            status.value = "Limpando arquivos temporários..."
            page.update()
            temp_files = await asyncio.to_thread(cleaner.clean_temp_files)
            result_cards.controls[0].content.controls[2].controls[1].value = f"{temp_files} arquivos removidos"
            page.update()
            
            # Encerra processos desnecessários
            progress_bar.value = 0.6
            status.value = "Encerrando processos desnecessários..."
            page.update()
            processes = await asyncio.to_thread(cleaner.terminate_unnecessary_processes)
            result_cards.controls[1].content.controls[2].controls[1].value = f"{processes} processos encerrados"
            page.update()
            
            # Limpa cache
            progress_bar.value = 0.9
            status.value = "Limpando cache..."
            page.update()
            cache = await asyncio.to_thread(cleaner.clean_cache)
            result_cards.controls[2].content.controls[2].controls[1].value = f"{cache} MB liberados"
            page.update()
            
            # Finaliza a limpeza
            progress_bar.value = 1.0
            status.value = "Limpeza concluída!"
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text("Limpeza do sistema concluída com sucesso!"),
                action="OK"
            ))
            
        except Exception as e:
            status.value = f"Erro durante a limpeza: {str(e)}"
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text(f"Erro durante a limpeza: {str(e)}"),
                action="OK"
            ))
            
        finally:
            # Esconde os indicadores de progresso
            progress_ring.visible = False
            progress_bar.visible = False
            progress_bar.value = 0
            page.update()

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
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    }
    
    analyze_button = ft.ElevatedButton(
        "Analisar",
        on_click=handle_analyze_click,
        icon=ft.icons.SEARCH,
        **button_style
    )
    
    start_button = ft.ElevatedButton(
        "Limpar",
        on_click=handle_clean_click,
        icon=ft.icons.CLEANING_SERVICES,
        **button_style
    )
    
    whitelist_button = ft.ElevatedButton(
        "Whitelist",
        on_click=handle_whitelist_click,
        icon=ft.icons.LOCK,
        **button_style
    )
    
    result_cards = ft.Row(
        [
            create_result_card("Arquivos Temporários", 0, ft.icons.FOLDER_OUTLINED, width=250),
            create_result_card("Processos Desnecessários", 0, ft.icons.APPS, width=250),
            create_result_card("Cache", 0, ft.icons.STORAGE_ROUNDED, width=250),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    tabs = ft.Tabs(
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
                            ft.Row(
                                [progress_ring, progress_bar], 
                                spacing=10, 
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
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