import pygame

keyboard_mapping = (
    {"act": pygame.K_RIGHT, "input": ("right",)},
    {"act": pygame.K_LEFT, "input": ("left",)},
    {"act": pygame.K_UP, "input": ("up",)},
    {"act": pygame.K_DOWN, "input": ("down",)},
    {"act": pygame.K_e, "input": ("R2",)},
    {"act": pygame.K_w, "input": ("B",)},
    {"act": pygame.K_q, "input": ("A",)},
    {"act": pygame.K_d, "input": ("R1",)},
    {"act": pygame.K_s, "input": ("Y",)},
    {"act": pygame.K_a, "input": ("X",)},
    {"act": pygame.K_r, "input": ("A", "B", "R2")},
    {"act": pygame.K_f, "input": ("X", "Y", "R1")},
    {"act": pygame.K_1, "input": ("Level_1",)},
    {"act": pygame.K_2, "input": ("Level_2",)},
    {"act": pygame.K_3, "input": ("Level_3",)},
    {"act": pygame.K_RETURN, "input": ("return",)},
)

AI_mapping = (
    {"input": ("right",)},
    {"input": ("left",)},
    {"input": ("up",)},
    {"input": ("down",)},
    {"input": ("R2",)},
    {"input": ("B",)},
    {"input": ("A",)},
    {"input": ("R1",)},
    {"input": ("Y",)},
    {"input": ("X",)},
    {"input": ("return",)},
)

controller_mapping = (
    {
        "act": pygame.CONTROLLER_AXIS_LEFTX,
        "input": [
            "right",
        ],
        "tipe": "axis",
        "dir": 1,
        "deadzone": 0.6,
    },
    {
        "act": pygame.CONTROLLER_AXIS_LEFTX,
        "input": [
            "left",
        ],
        "tipe": "axis",
        "dir": -1,
        "deadzone": 0.6,
    },
    {
        "act": pygame.CONTROLLER_AXIS_LEFTY,
        "input": [
            "up",
        ],
        "tipe": "axis",
        "dir": -1,
        "deadzone": 0.6,
    },
    {
        "act": pygame.CONTROLLER_AXIS_LEFTY,
        "input": [
            "down",
        ],
        "tipe": "axis",
        "dir": 1,
        "deadzone": 0.6,
    },
    {
        "act": pygame.CONTROLLER_BUTTON_X,
        "input": [
            "X",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_Y,
        "input": [
            "Y",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
        "input": [
            "R1",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_A,
        "input": [
            "A",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_B,
        "input": [
            "B",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_AXIS_TRIGGERRIGHT,
        "input": [
            "R2",
        ],
        "tipe": "axis",
        "dir": 1,
        "deadzone": 0.5,
    },
    {
        "act": pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
        "input": ["Y", "B"],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_AXIS_TRIGGERLEFT,
        "input": ["R1", "R2"],
        "tipe": "axis",
        "dir": 1,
        "deadzone": 0.5,
    },
    {
        "act": pygame.CONTROLLER_BUTTON_BACK,
        "input": [
            "escape",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_START,
        "input": [
            "return",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_DPAD_RIGHT,
        "input": [
            "right",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_DPAD_LEFT,
        "input": [
            "left",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_DPAD_UP,
        "input": [
            "up",
        ],
        "tipe": "button",
    },
    {
        "act": pygame.CONTROLLER_BUTTON_DPAD_DOWN,
        "input": [
            "down",
        ],
        "tipe": "button",
    },
)
