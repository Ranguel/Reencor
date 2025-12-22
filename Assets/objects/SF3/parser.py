import json

dir = "/Users/roberto/Documents/Python/Reencor/Assets/objects/SF3/"

name = "Sparks"


class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            formatted_items = []

            for key, value in obj.items():
                # Especial para "states"
                if isinstance(value, dict) and key == "states":
                    formatted_states = []
                    for state_key, state_val in value.items():
                        # Cada propiedad del estado en una línea
                        state_lines = []
                        for prop_key, prop_val in state_val.items():
                            compact_value = json.dumps(prop_val, separators=(",", ": "))
                            state_lines.append(f'    "{prop_key}": {compact_value}')
                        state_block = (
                            '  "'
                            + state_key
                            + '": {\n'
                            + ",\n".join(state_lines)
                            + "\n  }"
                        )
                        formatted_states.append(state_block)
                    formatted_value = "{\n" + ",\n".join(formatted_states) + "\n}"

                elif isinstance(value, dict):
                    # Para otros diccionarios
                    formatted_value = json.dumps(value, separators=(",", ": "))

                else:
                    formatted_value = json.dumps(value, separators=(",", ": "))

                formatted_items.append(f'"{key}": {formatted_value}')

            return "{\n  " + ",\n  ".join(formatted_items) + "\n}"

        return super().encode(obj)


def recursive_update_boxes(obj):
    if isinstance(obj, dict):
        for key in list(obj.keys()):  # ← COPIA segura de las llaves
            value = obj[key]

            if (
                key == "boxes"
                and isinstance(value, list)
                and all(isinstance(b, list) and len(b) == 4 for b in value)
            ):
                obj[key] = [{"rect": b} for b in value]

            elif key == "image_size":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["size"] = value
                else:
                    obj["draw"] = [{"size": value}]
                del obj[key]

            elif key == "image_offset":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["offset"] = value
                else:
                    obj["draw"] = [{"offset": value}]
                del obj[key]

            elif key == "image_angle":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["rotation"] = value
                else:
                    obj["draw"] = [{"rotation": value}]
                del obj[key]

            elif key == "image_mirror":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["flip"] = value
                else:
                    obj["draw"] = [{"flip": value}]
                del obj[key]

            elif key == "image_tint":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["tint"] = value
                else:
                    obj["draw"] = [{"tint": value}]
                del obj[key]

            elif key == "image_repeat":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["repeat"] = value
                else:
                    obj["draw"] = [{"repeat": value}]
                del obj[key]

            elif key == "image_glow":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["glow"] = value
                else:
                    obj["draw"] = [{"glow": value}]
                del obj[key]

            elif key == "image":
                if obj.get("draw", None) != None:
                    obj["draw"][0]["file"] = value
                else:
                    obj["draw"] = [{"file": value}]
                del obj[key]

            elif key in {"set_pos_on_hit", "pos_offset", "influence_pos"}:
                obj[key] = {"position": value}

            else:
                recursive_update_boxes(value)

    elif isinstance(obj, list):
        for item in obj:
            recursive_update_boxes(item)


def delete_keys(obj, keys_to_delete):
    if isinstance(obj, dict):
        for key in keys_to_delete:
            if key in obj:
                del obj[key]
        for value in obj.values():
            delete_keys(value, keys_to_delete)
    elif isinstance(obj, list):
        for item in obj:
            delete_keys(item, keys_to_delete)


def move_condition_to_state(obj):
    for condition in obj.get("conditions", []):

        trigg = dict(condition)
        trigg.pop("state", None)

        obj["states"][condition["state"]] = {
            "condition": trigg,
            **obj["states"].get(condition["state"], {}),
        }


def transform_create_object(data):
    if isinstance(data, dict):
        # Si es un diccionario, procesamos cada valor recursivamente
        for key, value in list(data.items()):
            if key == "create_object" and isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, list) and len(item) >= 2:
                        obj_dict = {"dict": item[0], "position": item[1]}
                        # Tercer elemento → angle
                        if len(item) > 2 and item[2] != [0, 0, 0]:
                            obj_dict["rotation"] = item[2]
                        # Cuarto elemento → state
                        if len(item) > 3 and item[3] != 0:
                            obj_dict["state"] = item[3]
                        # Quinto elemento → palette
                        if len(item) > 4 and item[4] != 0:
                            obj_dict["palette"] = item[4]
                        new_list.append(obj_dict)
                data[key] = new_list
            else:
                transform_create_object(value)  # Recursión para otros valores
    elif isinstance(data, list):
        # Si es lista, procesar cada elemento
        for i, item in enumerate(data):
            transform_create_object(item)


def transform_meters(data):
    if isinstance(data, dict):
        keys_to_remove = []
        meters_to_add = {}

        for key, value in data.items():
            # Buscar recursivamente en valores
            transform_meters(value)

            if (
                key in ("damage", "stamina")
                and isinstance(value, list)
                and len(value) >= 1
            ):
                # "damage" y "stamina": value = [hit, block], solo para "other"
                hit_val = value[0]
                block_val = value[1] if len(value) > 1 else 0

                meter_name = "health" if key == "damage" else "stamina"
                meter_dict = {}

                if hit_val != 0:
                    meter_dict.setdefault("hit", {})["other"] = hit_val
                if block_val != 0:
                    meter_dict.setdefault("block", {})["other"] = block_val

                if meter_dict:
                    meters_to_add[meter_name] = meter_dict
                keys_to_remove.append(key)

            elif key == "hit_bar_gain" and isinstance(value, list) and len(value) >= 2:
                # "hit_bar_gain": value = [[self_hit, self_block], [other_hit, other_block]]
                self_vals = value[0]
                other_vals = value[1]

                meter_dict = {}
                # hit
                hit_subdict = {}
                if len(self_vals) > 0 and self_vals[0] != 0:
                    hit_subdict["self"] = self_vals[0]
                if len(other_vals) > 0 and other_vals[0] != 0:
                    hit_subdict["other"] = other_vals[0]
                if hit_subdict:
                    meter_dict["hit"] = hit_subdict

                # block
                block_subdict = {}
                if len(self_vals) > 1 and self_vals[1] != 0:
                    block_subdict["self"] = self_vals[1]
                if len(other_vals) > 1 and other_vals[1] != 0:
                    block_subdict["other"] = other_vals[1]
                if block_subdict:
                    meter_dict["block"] = block_subdict

                if meter_dict:
                    meters_to_add["super"] = meter_dict
                keys_to_remove.append(key)

        # Eliminar las llaves originales
        for k in keys_to_remove:
            data.pop(k, None)

        # Añadir o actualizar la llave "hit_meter"
        if meters_to_add:
            if "hit_meter" not in data or not isinstance(data["hit_meter"], dict):
                data["hit_meter"] = {}
            # Actualizar sin sobreescribir
            for meter_key, meter_val in meters_to_add.items():
                if meter_key not in data["hit_meter"]:
                    data["hit_meter"][meter_key] = meter_val
                else:
                    # Merge si ya existe
                    for res_key, res_val in meter_val.items():
                        if res_key not in data["hit_meter"][meter_key]:
                            data["hit_meter"][meter_key][res_key] = res_val
                        else:
                            # Merge subdiccionarios "self"/"other"
                            data["hit_meter"][meter_key][res_key].update(res_val)

    elif isinstance(data, list):
        for item in data:
            transform_meters(item)


def replace_hitstun(d):
    if isinstance(d, dict):
        keys_to_replace = []
        for k, v in d.items():
            if k == "hitstun":
                keys_to_replace.append(k)
            else:
                replace_hitstun(v)

        for k in keys_to_replace:
            value = d[k]
            if isinstance(value, list) and len(value) == 2:
                d[k] = {"hit": value[0], "block": value[1]}

    elif isinstance(d, list):
        for item in d:
            replace_hitstun(item)


box_types = [
    "hurtbox",
    "hitbox",
    "pushbox",
    "takebox",
    "grabbox",
    "triggerbox",
    "environmentbox",
]


def recover_boxes_format(old, new):
    for state in old["states"]:
        for sub_index, sub_state in enumerate(old["states"][state]["framedata"]):
            for box_type in box_types:
                if box_type in sub_state:
                    old["states"][state]["framedata"][sub_index][box_type].pop("boxes")
                    new["states"][state]["framedata"][sub_index]["boxes"][box_type] = {
                        "rects": new["states"][state]["framedata"][sub_index]["boxes"][
                            box_type
                        ]["rects"],
                        **old["states"][state]["framedata"][sub_index][box_type],
                    }


def transform_boxes_format(data: dict):
    """
    Convierte framedata de:
    [{"hitbox": {"boxes": ...}, "hurtbox": {"boxes": ...}, ...}]
    a:
    [{"boxes": {"hitbox": {"rects": ...}, "hurtbox": {"rects": ...}, ...}}]
    Mantiene las demás llaves dentro de cada tipo de box.
    """
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if key == "framedata" and isinstance(value, list):
                new_framedata = []
                for frame in value:
                    if isinstance(frame, dict):
                        boxes_dict = {}
                        other_data = {}
                        for sub_key, sub_value in frame.items():
                            if isinstance(sub_value, dict) and "boxes" in sub_value:
                                # Copiar todos los datos del box
                                box_data = dict(sub_value)
                                # Renombrar "boxes" → "rects"
                                box_data["rects"] = box_data.pop("boxes")
                                boxes_dict[sub_key] = box_data
                            else:
                                other_data[sub_key] = sub_value
                        if boxes_dict:
                            other_data["boxes"] = boxes_dict
                        new_framedata.append(other_data)
                    else:
                        new_framedata.append(frame)
                data[key] = new_framedata
            else:
                transform_boxes_format(value)

    elif isinstance(data, list):
        for item in data:
            transform_boxes_format(item)


def replace_hitstop(d):
    if isinstance(d, dict):
        keys_to_replace = []
        for k, v in d.items():
            if k == "hitstop":
                keys_to_replace.append(k)
            else:
                replace_hitstop(v)

        for k in keys_to_replace:
            value = d[k]
            d[k] = {"hit": value, "block": value, "parry": {"self": 16, "other": 14}}

    elif isinstance(d, list):
        for item in d:
            replace_hitstop(item)


def condition_dict_to_list(data):
    for state in data["states"]:
        if "condition" in data["states"][state]:
            condition = data["states"][state]["condition"]
            if isinstance(condition, dict):
                list_condition = []
                for key in condition:
                    if key == "state_current":
                        list_condition.append("state=" + condition[key][0])
                    else:
                        list_condition += condition[key]

                data["states"][state]["condition"] = list_condition
            else:
                data["states"][state]["condition"] = []


def transform_speed(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):  # iteramos sobre una copia
            if key == "speed" and isinstance(value, list) and len(value) >= 2:
                data["speed"] = {"vec": [value[0], value[1]]}
                del data[key]

            elif key == "add_speed" and isinstance(value, list) and len(value) >= 2:
                data["speed"] = {"vec": [value[0], value[1]], "type": "add"}
                del data[key]

            elif key == "con_speed" and isinstance(value, list) and len(value) >= 2:
                data["speed"] = {"vec": [value[0], value[1]], "type": "constant"}
                del data[key]

            elif key == "accel" and isinstance(value, list) and len(value) >= 2:
                data["accel"] = {"vec": [value[0], value[1]]}

            elif (
                key == "set_pos_on_hit" and isinstance(value, list) and len(value) >= 2
            ):
                data["set_pos_on_hit"] = {"vec": [value[0], value[1]]}

            elif key == "knockback" and isinstance(value, dict):
                data["knockback"] = {"hit": {}}
                for i in value:
                    if len(value) == 1 and i == "grounded":
                        data["knockback"] = {"vec": [value[i][0], value[i][1]]}
                    else:
                        data["knockback"]["hit"][i] = {
                            "vec": [value[i][0], value[i][1]]
                        }

            else:
                transform_speed(value)  # recursión
    elif isinstance(data, list):
        for item in data:
            transform_speed(item)


def normalize_boxes(data):
    """Normaliza la estructura de boxes asegurando que hitbox (y otros box types) estén directamente bajo 'boxes'."""
    if isinstance(data, dict):
        # Copiamos llaves para no modificar durante la iteración
        keys = list(data.keys())

        for key in keys:
            if key == "boxes" and isinstance(data[key], dict):
                box_dict = data[key]

                # Recorremos tipos de box conocidos
                for box_type in [
                    "hitbox",
                    "hurtbox",
                    "pushbox",
                    "grabbox",
                    "triggerbox",
                ]:
                    if box_type in box_dict:
                        inner = box_dict[box_type]

                        # Caso: "hitbox": {"hitbox": {...}}
                        if isinstance(inner, dict) and box_type in inner:
                            box_dict[box_type] = inner[box_type]

                        # Recursión dentro del valor ya limpio
                        normalize_boxes(box_dict[box_type])

            else:
                normalize_boxes(data[key])

    elif isinstance(data, list):
        for item in data:
            normalize_boxes(item)


def normalize_vec(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if (key == "vec" or key == "offset" or key == "size") and isinstance(
                value, list
            ):
                # dividir cada valor entre 100
                data[key] = [v / 100 for v in value if isinstance(v, (int, float))]
            else:
                normalize_vec(value)  # recursion
    elif isinstance(data, list):
        for item in data:
            normalize_vec(item)


def change_grounded_format(data):
    for state in data["states"]:
        if "state" in data["states"][state]:
            if data["states"][state]["state"] == "grounded":
                data["states"][state]["grounded"] = True
            elif data["states"][state]["state"] == "airborne":
                data["states"][state]["grounded"] = False
        else:
            data["states"][state]["grounded"] = True

        data["states"][state].pop("state", None)

new=[]
def transform_hit_type_data(data):
    for state in data["states"]:

        for ind, hit_type in enumerate(data["states"][state].get("condition", [])):
            
            if isinstance(data["states"][state]["condition"], list):

                if hit_type in {"super", "special", "heavy", "medium", "light"}:
                    data["states"][state]["condition"][ind] = "strength=" + hit_type
                elif hit_type in {"high", "middle", "low"}:
                    data["states"][state]["condition"][ind]  = "level=" + hit_type

                elif hit_type in {
                    "uppercut"
                    "jaw",
                    "body",
                    "trip",
                    "solarplex",
                    "hook",
                }:
                    data["states"][state]["condition"][ind] = "reaction=" + hit_type
                    data["states"][state]["condition"] += ["tumble=True"]


        for substate in data["states"][state]["framedata"]:
            if "boxes" in substate:
                if substate["boxes"].get("hitbox", False):
                    if substate["boxes"]["hitbox"].get("hit_meter", False):
                        if substate["boxes"]["hitbox"]["hit_meter"].get(
                            "health", False
                        ):
                            substate["boxes"]["hitbox"]["damage"] = substate["boxes"][
                                "hitbox"
                            ]["hit_meter"]["health"]["hit"]["other"]
                            substate["boxes"]["hitbox"]["hit_meter"].pop("health", None)

                        if substate["boxes"]["hitbox"]["hit_meter"].get(
                            "stamina", False
                        ):
                            substate["boxes"]["hitbox"]["stamina"] = substate["boxes"][
                                "hitbox"
                            ]["hit_meter"]["stamina"]["hit"]["other"]
                            substate["boxes"]["hitbox"]["hit_meter"].pop(
                                "stamina", None
                            )

                    if substate["boxes"]["hitbox"].get("hit_type", False):
                        for hit_type in substate["boxes"]["hitbox"]["hit_type"]:
                            if hit_type in {
                                "super",
                                "special",
                                "heavy",
                                "medium",
                                "light",
                            }:
                                substate["boxes"]["hitbox"]["strength"] = hit_type
                            elif hit_type in {"high", "middle", "low"}:
                                substate["boxes"]["hitbox"]["level"] = hit_type
                            else:
                                substate["boxes"]["hitbox"]["reaction"] = hit_type
                                substate["boxes"]["hitbox"]["tumble"] = True
                            substate["boxes"]["hitbox"].pop("hit_type", None)

                    if substate["boxes"]["hitbox"].get("hitstop", False):
                        hitstop = substate["boxes"]["hitbox"]["hitstop"]
                        if isinstance(hitstop, dict):
                            stoplist = list(hitstop.values())
                            try:
                                if len(set(stoplist)) == 1:
                                    substate["boxes"]["hitbox"]["hitstop"] = stoplist[0]
                            except:
                                print(hitstop)
                                exit()


def transform_create_object(data):
    for state in data["states"]:
        for substate in data["states"][state]["framedata"]:
            if "create_object" in substate:
                for ob in substate["create_object"]:
                    if "vec" in ob:
                        ob["position"] = {"vec": ob["vec"]}
                        ob.pop("vec")


def transform_condition(data):
    for state in data["states"]:
        if "condition" in data["states"][state]:
            data["states"][state]["condition"] = [data["states"][state]["condition"],]
       


with open(dir + name + ".json", "r") as f:
    data = json.load(f)

# with open(old_r, "r") as f:
# old = json.load(f)

# recursive_update_boxes(data)

# delete_keys(data, ["command"])

# move_condition_to_state(data)

# transform_create_object(data)

# transform_meters(data)

# transform_boxes_format(old, data)

# transform_meters(data)

# transform_speed(data)

# normalize_boxes(data)

# normalize_vec(data)

# change_grounded_format(data)

#transform_hit_type_data(data)

transform_condition(data)

json_string = json.dumps(data, cls=CustomJSONEncoder)
with open(dir + name + "2.json", "w") as f:
    f.write(json_string)
