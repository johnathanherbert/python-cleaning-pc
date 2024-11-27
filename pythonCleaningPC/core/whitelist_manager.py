import json
import os

class WhitelistManager:
    def __init__(self):
        self.whitelist_file = "config/whitelist.json"
        self.default_processes = {
            # Processos do sistema Windows
            "System", "System Idle Process", "Registry", "smss.exe", "csrss.exe",
            "wininit.exe", "services.exe", "lsass.exe", "winlogon.exe", "explorer.exe",
            "dwm.exe", "svchost.exe", "spoolsv.exe", "RuntimeBroker.exe",
            
            # Processos de desenvolvimento
            "Code.exe",  # VSCode
            "code.exe",
            "vsls-agent.exe",  # VSCode Live Share
            "git.exe",
            "python.exe",
            "pythonw.exe",
            "node.exe",
            "cmd.exe",
            "powershell.exe",
            
            # Processos de segurança
            "MsMpEng.exe",  # Windows Defender
            "SecurityHealthService.exe",
            
            # Processos de hardware
            "dasHost.exe",  # Device Association Framework
            "fontdrvhost.exe",
            "atieclxx.exe",  # AMD Driver
            "atiesrxx.exe",  # AMD Driver
            
            # Processos de rede
            "mDNSResponder.exe",
            
            # Processos do Windows Update
            "TiWorker.exe",
            "WUDFHost.exe",
            "updatesvc.exe",
            
            # Processos de interface
            "sihost.exe",
            "taskhostw.exe",
            "ctfmon.exe",
            "TextInputHost.exe",
            
            # Processos de memória
            "MemCompression",
            
            # Processos de áudio
            "audiodg.exe",
            
            # Processos de energia
            "EABackgroundService.exe",
        }
        self.whitelisted_processes = set()
        self._ensure_config_dir()
        self.load_whitelist()

    def _ensure_config_dir(self):
        """Garante que o diretório config existe"""
        os.makedirs(os.path.dirname(self.whitelist_file), exist_ok=True)

    def load_whitelist(self):
        """Carrega a whitelist do arquivo ou cria uma nova se não existir"""
        try:
            with open(self.whitelist_file, 'r') as f:
                data = json.load(f)
                self.whitelisted_processes = set(data.get("processes", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self.whitelisted_processes = set()
            self.save_whitelist()

    def save_whitelist(self):
        """Salva a whitelist atual no arquivo"""
        with open(self.whitelist_file, 'w') as f:
            json.dump({"processes": list(self.whitelisted_processes)}, f, indent=4)

    def add_process(self, process_name):
        """Adiciona um processo à whitelist"""
        if process_name and process_name not in self.whitelisted_processes:
            self.whitelisted_processes.add(process_name)
            self.save_whitelist()
            return True
        return False

    def remove_process(self, process_name):
        """Remove um processo da whitelist"""
        if process_name in self.whitelisted_processes:
            self.whitelisted_processes.remove(process_name)
            self.save_whitelist()
            return True
        return False

    def get_processes(self):
        """Retorna a lista de processos na whitelist"""
        return list(self.whitelisted_processes)

    def is_whitelisted(self, process_name):
        """Verifica se um processo está na whitelist"""
        return process_name in self.whitelisted_processes or process_name in self.default_processes

    def is_default_process(self, process_name):
        """Verifica se um processo é um processo padrão"""
        return process_name in self.default_processes