import os
import tempfile
import psutil
import gzip
from utils.file_operations import walk_directory, remove_file
from core.whitelist_manager import WhitelistManager

class SystemCleaner:
    def __init__(self):
        self.files_removed = 0
        self.processes_terminated = 0
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

    def clean_temp_files(self):
        print("Iniciando limpeza de arquivos temporários...")
        self.files_removed = 0
        
        temp_dirs = [tempfile.gettempdir(), "C:\\Windows\\Temp"] if os.name == "nt" else ["/tmp"]
        for temp_dir in temp_dirs:
            print(f"Limpando diretório: {temp_dir}")
            if os.path.exists(temp_dir):
                for file_path in walk_directory(temp_dir):
                    try:
                        if not any(proc in file_path.lower() for proc in self.whitelist_manager.get_processes()):
                            if remove_file(file_path):
                                print(f"Arquivo removido: {file_path}")
                                self.files_removed += 1
                    except Exception as e:
                        print(f"Erro ao remover arquivo {file_path}: {e}")
                        continue

        print(f"Total de arquivos removidos: {self.files_removed}")
        return self.files_removed

    def clean_cache(self):
        print("Iniciando limpeza de cache...")
        cache_cleaned = 0
        
        cache_paths = [
            os.path.expanduser("~/.cache"),
            os.path.expanduser("~/AppData/Local/Temp") if os.name == "nt" else "/var/cache",
        ]
        
        for path in cache_paths:
            print(f"Limpando cache em: {path}")
            if os.path.exists(path):
                for file_path in walk_directory(path):
                    try:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            if remove_file(file_path):
                                print(f"Cache removido: {file_path} ({file_size // 1024} KB)")
                                cache_cleaned += file_size
                    except Exception as e:
                        print(f"Erro ao limpar cache {file_path}: {e}")
                        continue

        total_mb = cache_cleaned // (1024 * 1024)
        print(f"Total de cache limpo: {total_mb} MB")
        return total_mb

    def terminate_unnecessary_processes(self):
        print("Iniciando encerramento de processos desnecessários...")
        self.processes_terminated = 0
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                process_name = proc.info['name']
                if not self.whitelist_manager.is_whitelisted(process_name):
                    print(f"Tentando encerrar processo: {process_name}")
                    proc.terminate()
                    proc.wait(timeout=3)
                    print(f"Processo encerrado: {process_name}")
                    self.processes_terminated += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                print(f"Não foi possível encerrar {process_name}: {e}")
                continue
            except Exception as e:
                print(f"Erro ao processar {process_name}: {e}")
                continue

        print(f"Total de processos encerrados: {self.processes_terminated}")
        return self.processes_terminated

    def optimize_cache(self):
        print("Otimizando cache...")
        
        cache_paths = [
            os.path.expanduser("~/.cache"),
            os.path.expanduser("~/AppData/Local/Temp") if os.name == "nt" else "/var/cache",
        ]
        
        optimized_files = 0
        for path in cache_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Verifica se temos permissão para acessar o arquivo
                            if os.access(file_path, os.R_OK | os.W_OK):
                                # Exemplo: compactar arquivo
                                with open(file_path, 'rb') as f_in:
                                    with gzip.open(file_path + '.gz', 'wb') as f_out:
                                        f_out.writelines(f_in)
                                os.remove(file_path)  # Remove o arquivo original
                                optimized_files += 1
                            else:
                                print(f"Sem permissão para acessar {file_path}")
                        except Exception as e:
                            print(f"Erro ao otimizar arquivo {file_path}: {e}")
                            continue
        
        print(f"Cache otimizado: {optimized_files} arquivos compactados.")
        return f"Cache otimizado: {optimized_files} arquivos compactados."