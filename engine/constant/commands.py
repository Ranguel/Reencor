import json

with open("Assets/input/commands.json", "r") as f:
    commands_loaded = json.load(f)


def build_command_sequences(commands: dict) -> list:
    result = []

    def replace_dir(token: str, from_dir: str, to_dir: str) -> str:
        return token.replace(from_dir, to_dir)

    def transform_sequence(sequence, from_dir, to_dir):
        return tuple(
            tuple(replace_dir(token, from_dir, to_dir) for token in step)
            for step in sequence
        )

    for name, sequence in commands.items():
        flat = {token for step in sequence for token in step}
        uses_right = any("right" in token for token in flat)

        base_data = {}

        if uses_right:
            # RIGHT
            result.append(
                {
                    "name": f"{name}_right",
                    "sequence": sequence,
                    **base_data,
                }
            )

            # LEFT
            left_sequence = transform_sequence(sequence, "right", "left")
            result.append(
                {
                    "name": f"{name}_left",
                    "sequence": left_sequence,
                    **base_data,
                }
            )
        else:
            # Neutral command
            result.append(
                {
                    "name": name,
                    "sequence": sequence,
                    **base_data,
                }
            )

    return result


COMMAND_SEQUENCE = tuple(build_command_sequences(commands=commands_loaded))
