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

def create_result_card(task_name, result, task_icon, task_details=None, on_details_click=None):
    """
    Cria um card de resultado para exibir informações de uma tarefa
    """
    card_content = [
        ft.Icon(task_icon, size=30, color=ft.colors.BLUE_500),
        ft.Text(task_name, size=16, weight="bold", color=ft.colors.BLUE_900),
        ft.Text(str(result), size=14, color=ft.colors.BLACK),
    ]
    
    if task_details and on_details_click:
        card_content.append(
            ft.TextButton(
                "Ver Detalhes",
                on_click=on_details_click,
                icon=ft.icons.INFO_OUTLINE,
            )
        )
    
    return ft.Container(
        content=ft.Column(
            card_content,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=200,
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
        page.update()

    detail_items = []
    if "processos" in title.lower():
        detail_items.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "✅ Marque os processos que você quer MANTER em execução",
                            size=14,
                            weight="bold",
                            color=ft.colors.GREEN,
                        ),
                        ft.Text(
                            "❌ Processos não marcados serão ENCERRADOS durante a limpeza",
                            size=14,
                            color=ft.colors.RED,
                        ),
                        ft.Divider(),
                    ],
                ),
                padding=10,
            )
        )

        for detail in details:
            try:
                process_name = detail.split(" (PID:")[0].strip()
                is_whitelisted = analyzer.whitelist_manager.is_whitelisted(process_name)
                is_default = analyzer.whitelist_manager.is_default_process(process_name)
                
                detail_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Checkbox(
                                    value=is_whitelisted,
                                    data=process_name,
                                    on_change=on_checkbox_change,
                                    disabled=is_default,
                                ),
                                ft.Icon(
                                    ft.icons.LOCK if is_default else ft.icons.APPS,
                                    color=ft.colors.GREY_400 if is_default else ft.colors.BLUE,
                                    size=16,
                                ),
                                ft.Text(
                                    detail,
                                    size=12,
                                    color=ft.colors.GREY_400 if is_default else None,
                                ),
                                ft.Text(
                                    " (Processo do Sistema)" if is_default else "",
                                    size=10,
                                    italic=True,
                                    color=ft.colors.GREY_400,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=ft.padding.only(bottom=5),
                    )
                )
            except Exception as e:
                print(f"Erro ao processar processo {detail}: {e}")
    else:
        detail_items = [ft.Text(detail, size=12) for detail in details]

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Detalhes - {title}", size=20, weight="bold"),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.ListView(
                            controls=detail_items,
                            spacing=2,
                            padding=10,
                        ),
                        height=400,
                        width=600,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=10,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"Total de itens: {len(details)}", 
                                    size=14, 
                                    weight="bold",
                                    color=ft.colors.BLUE
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.icons.LOCK, color=ft.colors.GREY_400, size=16),
                                        ft.Text(
                                            "Processos do sistema (não podem ser encerrados)",
                                            size=12,
                                            color=ft.colors.GREY_400,
                                        ),
                                    ],
                                ) if "processos" in title.lower() else ft.Container(),
                            ],
                        ),
                        padding=10,
                    ),
                ],
            ),
            padding=20,
        ),
        actions=[
            ft.TextButton("Fechar", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dlg)
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

    # Seção de informações mais compacta
    info_section = ft.Container(
        content=ft.Column([
            ft.Text(
                "Gerenciamento de Processos",
                size=20,  # Reduzido o tamanho
                weight="bold",
                color=ft.colors.BLUE_900
            ),
            ft.Text(
                "Proteja processos importantes do sistema contra o encerramento automático",
                size=12,  # Reduzido o tamanho
                color=ft.colors.GREY_700
            ),
            ft.Divider(height=1, color=ft.colors.BLUE_100),
        ]),
        margin=ft.margin.only(bottom=10)  # Reduzido o margin
    )

    # Seção de whitelist com altura dinâmica e scroll
    whitelist_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.SHIELD_MOON_ROUNDED, color=ft.colors.GREEN, size=20),
                ft.Text("Processos Protegidos", size=14, weight="bold", color=ft.colors.GREEN),
            ]),
            ft.Container(
                content=process_list,
                padding=5,
                height=200,
                border=ft.border.all(1, ft.colors.GREEN_50),
                border_radius=8,
            ),
        ]),
        padding=10,
        border=ft.border.all(1, ft.colors.GREEN_100),
        border_radius=10,
        bgcolor=ft.colors.GREEN_50,
    )

    # Atualiza a seção de processos em execução
    running_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.APPS_ROUNDED, color=ft.colors.BLUE, size=20),
                ft.Text("Processos em Execução", size=14, weight="bold", color=ft.colors.BLUE),
                process_counter,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            search_input,
            running_processes_list,
        ]),
        padding=10,
        border=ft.border.all(1, ft.colors.BLUE_100),
        border_radius=10,
        bgcolor=ft.colors.BLUE_50,
    )

    # Container principal ajustado
    main_content = ft.Container(
        content=ft.Column(
            [
                whitelist_section,
                ft.Container(height=10),
                running_section,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        width=700,
        height=600,  # Aumentada um pouco a altura para acomodar o conteúdo
        padding=10,
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