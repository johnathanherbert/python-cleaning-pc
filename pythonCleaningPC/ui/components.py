import flet as ft
import asyncio
import time
import psutil

class AsyncTimer:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.is_running = False
        self._task = None

    async def _run(self):
        while self.is_running:
            await self.callback()
            await asyncio.sleep(self.interval)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run())

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

def create_result_card(task_name, result, task_icon, task_details=None, on_details_click=None, width=200, loading=False):
    """
    Cria um card de resultado para exibir informações de uma tarefa
    """
    # Determina a cor baseada no resultado
    def get_status_color(value):
        if isinstance(value, (int, float)):
            if value > 1000:  # Muito alto
                return ft.colors.RED_400
            elif value > 500:  # Médio
                return ft.colors.ORANGE_400
            else:  # Baixo
                return ft.colors.GREEN_400
        return ft.colors.BLUE_400

    status_color = get_status_color(result)
    
    card_content = [
        ft.Icon(task_icon, size=30, color=status_color),
        ft.Text(task_name, size=16, weight="bold", color=ft.colors.BLUE_900),
        ft.Row([
            ft.ProgressRing(color=status_color, width=16, height=16, visible=loading),
            ft.Text(str(result), size=14, color=status_color, weight="bold"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(
            content=ft.Text(
                "Alto" if status_color == ft.colors.RED_400 else
                "Médio" if status_color == ft.colors.ORANGE_400 else
                "Baixo",
                size=12,
                color=status_color
            ),
            padding=5,
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, status_color),
        )
    ]
    
    if task_details and on_details_click:
        card_content.append(
            ft.TextButton(
                "Ver Detalhes",
                on_click=on_details_click,
                icon=ft.icons.INFO_OUTLINE,
                style=ft.ButtonStyle(
                    color=status_color,
                ),
            )
        )
    
    return ft.Container(
        content=ft.Column(
            card_content,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=width,
        padding=20,
        border=ft.border.all(1, status_color),
        border_radius=10,
        bgcolor=ft.colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.BLACK12,
            offset=ft.Offset(2, 2),
        )
    )

def show_details_dialog(page: ft.Page, details, title, analyzer):
    def close_dlg(_):
        dlg.open = False
        page.update()

    def on_checkbox_change(e):
        process_name = e.control.data
        if e.control.value:
            analyzer.whitelist_manager.add_process(process_name)
        else:
            analyzer.whitelist_manager.remove_process(process_name)

    content = ft.Column(
        [
            ft.Text(
                "Detalhes da Análise",
                size=20,
                weight="bold",
                color=ft.colors.BLUE_900
            ),
            ft.Divider(height=1, color=ft.colors.BLUE_100),
            ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.INFO_OUTLINE,
                                color=ft.colors.BLUE_400
                            ),
                            title=ft.Text(detail),
                            trailing=ft.Checkbox(
                                data=detail.split()[0] if " " in detail else detail,
                                on_change=on_checkbox_change,
                                value=analyzer.whitelist_manager.is_whitelisted(
                                    detail.split()[0] if " " in detail else detail
                                )
                            ) if "PID" in detail else None
                        )
                        for detail in details
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    height=300,
                ),
                border=ft.border.all(1, ft.colors.BLUE_100),
                border_radius=10,
                padding=10,
            ),
        ],
        spacing=20,
    )

    dlg = ft.AlertDialog(
        title=ft.Text(title),
        content=content,
        actions=[
            ft.TextButton("Fechar", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dlg
    dlg.open = True
    page.update()

def create_whitelist_dialog(page: ft.Page, whitelist_manager, analyzer):
    update_timer = None

    def search_processes(e):
        """Filtra os processos baseado na busca"""
        update_running_processes()

    def start_process_monitor():
        """Inicia o monitoramento de processos"""
        nonlocal update_timer
        update_timer = page.timer_interval = 2.0  # Atualiza a cada 2 segundos
        update_running_processes()

    def stop_process_monitor():
        """Para o monitoramento de processos"""
        nonlocal update_timer
        if update_timer:
            page.timer_interval = None
            update_timer = None

    def on_window_event(e):
        """Manipula eventos da janela"""
        if e.data == "focus":
            update_running_processes()

    def update_running_processes():
        """Atualiza a lista de processos em execução"""
        try:
            # Obter todos os processos em execução
            all_running_processes = [proc.info['name'] for proc in psutil.process_iter(['name'])]
            
            # Obter processos na whitelist
            whitelisted = whitelist_manager.get_processes()
            
            # Filtrar processos
            search_query = search_input.content.value.lower() if search_input.content.value else ""
            filtered_processes = [
                proc for proc in all_running_processes 
                if (not search_query or search_query in proc.lower()) and proc not in whitelisted
            ]
            
            running_processes_list.controls = [
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.APPS_ROUNDED, color=ft.colors.BLUE),
                        title=ft.Text(proc),
                        subtitle=ft.Text("Em execução", size=12),
                        trailing=ft.IconButton(
                            ft.icons.ADD_CIRCLE_ROUNDED,
                            icon_color=ft.colors.BLUE_400,
                            data=proc,
                            on_click=add_process,
                            tooltip="Adicionar à whitelist"
                        )
                    ),
                    border=ft.border.all(1, ft.colors.BLUE_100),
                    border_radius=8,
                    margin=5,
                )
                for proc in filtered_processes
            ]
            
            process_counter.value = f"Processos em execução: {len(filtered_processes)}"
            page.update()
        except Exception as e:
            print(f"Erro ao atualizar processos: {e}")

    def update_process_list():
        """Atualiza a lista de processos protegidos (whitelist)"""
        processes = whitelist_manager.get_processes()
        process_list.controls = [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.SHIELD_MOON_ROUNDED, color=ft.colors.GREEN),
                    title=ft.Text(proc, weight="bold"),
                    subtitle=ft.Text("Processo protegido", size=12),
                    trailing=ft.IconButton(
                        ft.icons.DELETE_ROUNDED,
                        icon_color=ft.colors.RED_400,
                        data=proc,
                        on_click=remove_process,
                        tooltip="Remover da whitelist"
                    )
                ),
                border=ft.border.all(1, ft.colors.GREEN_100),
                border_radius=8,
                margin=5,
            )
            for proc in processes
        ]
        page.update()

    def close_dlg(_):
        stop_process_monitor()
        dlg.open = False
        page.update()

    def add_process(e):
        process_name = e.control.data
        if process_name:
            if whitelist_manager.add_process(process_name):
                # Atualiza ambas as listas
                update_process_list()
                update_running_processes()
                # Mostrar snackbar de confirmação
                page.show_snack_bar(ft.SnackBar(
                    content=ft.Text(f"Processo {process_name} adicionado à whitelist"),
                    action="OK"
                ))
                page.update()

    def remove_process(e):
        process_name = e.control.data
        whitelist_manager.remove_process(process_name)
        update_process_list()
        update_running_processes()
        # Mostrar snackbar de confirmação
        page.show_snack_bar(ft.SnackBar(
            content=ft.Text(f"Processo {process_name} removido da whitelist"),
            action="OK"
        ))
        page.update()

    # Containers para as listas
    process_list = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        spacing=0,
        height=180,
    )
    
    running_processes_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        height=250,
    )

    # Contador de processos
    process_counter = ft.Text(
        "Processos em execução: 0",
        size=12,
        color=ft.colors.BLUE_400,
        weight="bold"
    )

    # Campo de busca estilizado
    search_input = ft.Container(
        content=ft.TextField(
            label="Buscar processos",
            prefix_icon=ft.icons.SEARCH,
            on_change=search_processes,
            width=300,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.BLUE_50,
        ),
        margin=ft.margin.only(bottom=10)
    )

    # Container principal ajustado para layout horizontal
    main_content = ft.Container(
        content=ft.Row(
            [
                # Coluna da esquerda - Processos Protegidos
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.SHIELD_MOON_ROUNDED, color=ft.colors.GREEN, size=20),
                            ft.Text("Processos Protegidos", size=14, weight="bold", color=ft.colors.GREEN),
                        ]),
                        ft.Container(
                            content=process_list,
                            padding=5,
                            height=450,  # Aumentada a altura
                            width=340,   # Largura fixa
                            border=ft.border.all(1, ft.colors.GREEN_50),
                            border_radius=8,
                        ),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREEN_100),
                    border_radius=10,
                    bgcolor=ft.colors.GREEN_50,
                    expand=True,  # Permite expansão horizontal
                ),
                
                # Separador vertical
                ft.VerticalDivider(
                    width=1,
                    color=ft.colors.BLUE_100,
                ),
                
                # Coluna da direita - Processos em Execução
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.APPS_ROUNDED, color=ft.colors.BLUE, size=20),
                            ft.Text("Processos em Execução", size=14, weight="bold", color=ft.colors.BLUE),
                            process_counter,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        search_input,
                        ft.Container(
                            content=running_processes_list,
                            padding=5,
                            height=450,  # Aumentada a altura
                            width=340,   # Largura fixa
                            border=ft.border.all(1, ft.colors.BLUE_50),
                            border_radius=8,
                        ),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.BLUE_100),
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_50,
                    expand=True,  # Permite expansão horizontal
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=750,  # Aumentada a largura total
        height=550, # Aumentada a altura total
        padding=10,
    )

    # Ajuste no título do diálogo
    info_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.SHIELD, color=ft.colors.BLUE_900, size=24),
                ft.Text(
                    "Gerenciamento de Processos",
                    size=20,
                    weight="bold",
                    color=ft.colors.BLUE_900
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(
                "Proteja processos importantes do sistema contra o encerramento automático",
                size=12,
                color=ft.colors.BLUE_700,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(height=1, color=ft.colors.BLUE_100),
        ]),
        margin=ft.margin.only(bottom=10)
    )

    dlg = ft.AlertDialog(
        modal=True,
        title=info_section,
        content=main_content,
        actions=[
            ft.ElevatedButton(
                "Fechar",
                on_click=close_dlg,
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.BLUE_400,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Configura os eventos de atualização
    page.window.on_event = on_window_event
    start_process_monitor()

    # Atualização inicial
    update_process_list()
    update_running_processes()

    # Mostra o diálogo
    dlg.open = True
    page.update()

    return dlg