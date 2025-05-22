import os

def get_directory_structure(root_dir, indent=0):
    structure = ""
    for item in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, item)
        structure += " " * indent + "|-- " + item + "\n"
        if os.path.isdir(path):
            structure += get_directory_structure(path, indent + 4)
    return structure

root_directory = "C:/Users/valeriu.bistritchi/Desktop/E2E_Testing"  # Укажите путь к корневой папке
structure = get_directory_structure(root_directory)

# Записываем в файл
with open("directory_structure.txt", "w", encoding="utf-8") as f:
    f.write(structure)

print("Структура записана в directory_structure.txt")
