import os
import tempfile
import psutil
from utils.file_operations import walk_directory
from core.whitelist_manager import WhitelistManager

class SystemAnalyzer:
    def __init__(self):
        self.temp_files_count = 0
        self.unnecessary_processes_count = 0
        self.cache_size = 0
        self.temp_files_details = []
        self.unnecessary_processes_details = []
        self.cache_details = []
        self.whitelist_manager = WhitelistManager()

    def get_running_processes_names(self):
        """Retorna uma lista com os nomes dos processos em execução que estão na whitelist"""
        whitelisted_processes = set()
        for proc in psutil.process_iter(['name']):
            try:
                process_name = proc.info['name']
                if self.whitelist_manager.is_whitelisted(process_name):
                    whitelisted_processes.add(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return whitelisted_processes

    def should_preserve_file(self, file_path, whitelisted_processes):
        """Verifica se um arquivo deve ser preservado baseado nos processos em whitelist"""
        try:
            # Verifica se algum processo em whitelist está usando o arquivo
            for proc in psutil.process_iter(['name', 'open_files']):
                if proc.info['name'] in whitelisted_processes:
                    try:
                        open_files = proc.open_files()
                        if open_files:
                            for file in open_files:
                                if os.path.normpath(file.path) == os.path.normpath(file_path):
                                    return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Verifica se o nome do processo está no caminho do arquivo
            file_path_lower = file_path.lower()
            for proc_name in whitelisted_processes:
                proc_name_lower = proc_name.replace('.exe', '').lower()
                if proc_name_lower in file_path_lower:
                    return True
                
        except Exception as e:
            print(f"Erro ao verificar arquivo {file_path}: {e}")
        
        return False

    def analyze_temp_files(self):
        print("Iniciando análise de arquivos temporários...")
        self.temp_files_count = 0
        self.temp_files_details.clear()
        
        # Limite máximo de arquivos para análise
        MAX_FILES = 1000
        
        temp_dirs = [tempfile.gettempdir(), "C:\\Windows\\Temp"] if os.name == "nt" else ["/tmp"]
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for file_path in walk_directory(temp_dir):
                    try:
                        if self.temp_files_count >= MAX_FILES:
                            break
                        
                        if not any(proc in file_path.lower() for proc in self.whitelist_manager.get_processes()):
                            self.temp_files_count += 1
                            self.temp_files_details.append(file_path)
                    except Exception as e:
                        print(f"Erro ao analisar arquivo {file_path}: {e}")
                        continue

        print(f"Arquivos temporários encontrados: {self.temp_files_count}")
        return self.temp_files_count

    def analyze_unnecessary_processes(self):
        print("Iniciando análise de processos desnecessários...")
        self.unnecessary_processes_count = 0
        self.unnecessary_processes_details.clear()

        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    process_name = proc.info['name']
                    if not self.whitelist_manager.is_whitelisted(process_name):
                        self.unnecessary_processes_count += 1
                        self.unnecessary_processes_details.append(f"{process_name}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Erro ao analisar processos: {e}")

        return self.unnecessary_processes_count

    def analyze_cache(self):
        print("Iniciando análise de cache...")
        self.cache_size = 0
        self.cache_details.clear()
        
        # Limite máximo de arquivos para análise
        MAX_CACHE_FILES = 1000
        files_analyzed = 0
        
        cache_paths = [
            os.path.expanduser("~/.cache"),
            os.path.expanduser("~/AppData/Local/Temp") if os.name == "nt" else "/var/cache",
        ]

        for path in cache_paths:
            if os.path.exists(path):
                for file_path in walk_directory(path):
                    try:
                        if files_analyzed >= MAX_CACHE_FILES:
                            break
                        
                        file_size = os.path.getsize(file_path)
                        self.cache_size += file_size
                        self.cache_details.append(f"{file_path} ({file_size // 1024} KB)")
                        files_analyzed += 1
                    except Exception as e:
                        print(f"Erro ao analisar cache {file_path}: {e}")
                        continue

        return self.cache_size // (1024 * 1024)  # Convert to MB