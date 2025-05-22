import re
import json

class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            formatted_items = []
            for key, value in obj.items():
                if isinstance(value, dict) and key == "states":
                    formatted_states = ",\n    ".join(
                        f'"{k}": {json.dumps(v)}' for k, v in value.items())
                    formatted_value = "{\n    " + formatted_states + "\n}"
                elif isinstance(value, dict):
                    formatted_value = json.dumps(value, separators=(',', ': '))
                else:
                    formatted_value = json.dumps(
                        value, separators=(',', ': '))
                formatted_items.append(f'"{key}": {formatted_value}')
            return "{\n  " + ",\n  ".join(formatted_items) + "\n}"
        return super().encode(obj)

input_file = "/Users/robertogonzalez/Documents/Python 2/Reencor 0.2/Assets/objects/ken SF3.json"
output_file = "/Users/robertogonzalez/Documents/Python 2/Reencor 0.2/Assets/objects/ken SF3.json"

OFFSET = 12064

def procesar(obj):
    if isinstance(obj, dict):
        nuevo_dict = {}
        for key, value in obj.items():
            if key in ("voice", "sound"):
                continue
            if key == "image" and isinstance(value, str):
                match = re.match(r"(11_Ken)/(\d{5})", value)
                if match:
                    base, numero = match.groups()
                    nuevo_valor = f"{base}/{int(numero) + OFFSET}"
                    nuevo_dict[key] = nuevo_valor
                    continue
            nuevo_dict[key] = procesar(value)
        return nuevo_dict
    elif isinstance(obj, list):
        return [procesar(item) for item in obj]
    else:
        return obj

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

resultado = procesar(data)

with open(output_file, 'w') as outfile:
    outfile.write(CustomJSONEncoder().encode(resultado))

print(f"✅ Archivo modificado guardado como '{output_file}'")