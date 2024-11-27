import psutil
import ctypes
from datetime import datetime
import os

class MemoryManager:
    def __init__(self):
        self.memory_info = {}
        self.update_memory_info()

    def update_memory_info(self):
        """Atualiza as informações de memória"""
        mem = psutil.virtual_memory()
        self.memory_info = {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'cached': getattr(mem, 'cached', 0),
            'buffers': getattr(mem, 'buffers', 0)
        }

    def get_memory_usage(self):
        """Retorna o uso de memória por processo"""
        process_memory = []
        for proc in psutil.process_iter(['name', 'memory_percent', 'memory_info']):
            try:
                proc_info = proc.as_dict(attrs=['name', 'memory_percent', 'memory_info'])
                memory_mb = proc_info['memory_info'].rss / (1024 * 1024)  # Converter para MB
                if memory_mb > 1:  # Filtrar processos usando mais de 1MB
                    process_memory.append({
                        'name': proc_info['name'],
                        'memory_percent': proc_info['memory_percent'],
                        'memory_mb': memory_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(process_memory, key=lambda x: x['memory_mb'], reverse=True)

    def clean_memory(self):
        """Libera memória RAM não utilizada"""
        # Em sistemas Windows, podemos usar EmptyWorkingSet para liberar memória
        if hasattr(ctypes.windll, 'psapi'):
            clear_count = 0
            for proc in psutil.process_iter(['pid']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
                        clear_count += 1
                except:
                    continue
            return f"Memória limpa: {clear_count} processos otimizados."
        return "Limpeza de memória não suportada neste sistema."

    def optimize_memory(self):
        """Otimiza o uso de memória RAM"""
        # Tenta liberar caches e buffers, se possível
        try:
            # Em sistemas Linux, podemos tentar liberar caches usando o comando 'sync' e 'echo 3 > /proc/sys/vm/drop_caches'
            if os.name != 'nt':
                os.system('sync; echo 3 > /proc/sys/vm/drop_caches')
                return "Otimização de memória concluída: caches liberados."
            else:
                # Em sistemas Windows, podemos tentar liberar memória de trabalho
                return self.clean_memory()
        except Exception as e:
            return f"Erro durante a otimização de memória: {e}"

    def get_memory_stats(self):
        """Retorna estatísticas de memória formatadas"""
        self.update_memory_info()
        return {
            'total': f"{self.memory_info['total'] / (1024**3):.2f} GB",
            'used': f"{self.memory_info['used'] / (1024**3):.2f} GB",
            'available': f"{self.memory_info['available'] / (1024**3):.2f} GB",
            'percent': f"{self.memory_info['percent']}%"
        }