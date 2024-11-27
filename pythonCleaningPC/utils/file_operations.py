import os

def walk_directory(directory):
    """
    Percorre um diretório recursivamente e retorna o caminho de cada arquivo encontrado.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def remove_file(file_path):
    """
    Remove um arquivo e retorna True se a operação foi bem-sucedida.
    """
    try:
        os.remove(file_path)
        return True
    except:
        return False