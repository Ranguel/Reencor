import math


def world_rect(obj, rect):
    x = (
        obj.position[0]
        + rect[0] * obj.scale[0] * (1 if obj.rotation[1] == 0 else -1)
        - rect[2] * obj.scale[0] * (obj.rotation[1] == 180)
    )
    y = obj.position[1] + rect[1] * obj.scale[1]
    return x, y, rect[2] * obj.scale[0], rect[3] * obj.scale[1]


def rect_collide(self, other, s_rect=None, o_rect=None):
    if not s_rect or not o_rect:
        return False
    if s_rect[2] <= 0 or s_rect[3] <= 0:
        return False
    if o_rect[2] <= 0 or o_rect[3] <= 0:
        return False

    (r1x, r1y, r1w, r1h), (r2x, r2y, r2w, r2h) = world_rect(self, s_rect), world_rect(
        other, o_rect
    )

    if not (
        r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y
    ):
        return False
    pen = {
        "right": (r1x + r1w) - r2x,
        "left": (r2x + r2w) - r1x,
        "down": (r1y + r1h) - r2y,
        "up": (r2y + r2h) - r1y,
    }
    direction = min(pen, key=pen.get)
    inter_left = max(r1x, r2x)
    inter_right = min(r1x + r1w, r2x + r2w)
    inter_top = max(r1y, r2y)
    inter_bottom = min(r1y + r1h, r2y + r2h)
    center = (
        (inter_left + inter_right) * 0.5,
        (inter_top + inter_bottom) * 0.5,
    )

    return direction, center, r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def find_object_by_direccional_input(
    index: int = 0, items: list = [], direction: list = [0, 0], min_dot=0.001
):
    """
    direction: vector normalizado (x, y)
    """

    best_item = index
    best_score = -math.inf

    cx, cy = items[index].position
    dx, dy = direction

    for number, item in enumerate(items):
        if number == index:
            continue

        vx = item.position[0] - cx
        vy = item.position[1] - cy

        dist = math.hypot(vx, vy)
        if dist == 0:
            continue

        nx = vx / dist
        ny = vy / dist

        dot = nx * dx + ny * dy
        if dot <= min_dot:
            continue
        forward = dot

        score = forward / dist

        if score > best_score:
            best_score = score
            best_item = number

    return best_item
