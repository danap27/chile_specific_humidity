import os


def sort_model_files_by_folder(data_path):
    """
    Separa los archivos .nc en carpetas por modelo.
    """
    # Listamos los archivos que hay en el directorio con extension .nc
    files = [f for f in os.listdir(data_path) if f.endswith('.nc')]
    if len(files) == 0:
        print('No hay archivos .nc en el directorio.')
        return
    # Iteramos sobre los archivos
    for f in files:
        # Separamos los nombres de los archivos por el caracter '_'
        # y nos quedamos con todos los elementos menos el ultimo
        # que es la extension .nc
        name = f.split('_')[:-1]
        # Unimos los elementos de la lista con el caracter '_'
        # para obtener el nombre del modelo
        model = '_'.join(name)
        # Creamos el directorio del model si no existe
        if not os.path.exists(os.path.join(data_path, model)):
            os.makedirs(os.path.join(data_path, model))
        # Movemos el archivo a la carpeta correspondiente
        os.rename(os.path.join(data_path, f), os.path.join(data_path, model, f))
        print(f'Archivo {f} movido a {model}')
    print('Archivos movidos correctamente.')

def print_tree_folders(path):
    """
    Imprime la estructura de directorios de un directorio dado.
    Ignora los archivos sueltos
    """
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)

sort_model_files_by_folder('./cordex_models')

