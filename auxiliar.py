import os

base_dir = "cordex_models/historical"
variable_principal = "huss"

result_dict = {}

for root, dirs, files in os.walk(base_dir):
    if root.endswith(variable_principal):
        model_name = os.path.basename(root)
        aux_vars = set()
        for dir_name in dirs:
            if dir_name != variable_principal:
                aux_vars.add(dir_name)
        num_aux_vars = len(aux_vars)
        if num_aux_vars not in result_dict:
            result_dict[num_aux_vars] = []
        result_dict[num_aux_vars].append(model_name)

print(result_dict)
