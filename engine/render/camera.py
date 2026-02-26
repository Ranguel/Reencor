import glm

from engine.math.vector import rotate_vector, normalize_length
from engine.math.geometry import clamp
from engine.effect.shake import ShakeComponent


class Camera:
    def __init__(self, aspect, position=(0, 0, 0), target=(0, 0, 0), smoothness=0.1):
        self.type = "camera"
        self.dimension = 3
        self.position = glm.vec3(position)
        self.target = glm.vec3(target)

        self.aspect = aspect
        self.view = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))
        self.projection = glm.perspective(glm.radians(50.0), aspect, 0.01, 50.0)

        self.smoothness = smoothness

        self.next_position = [0, 0, 0]
        self.next_target = [0, 0, 0]

        self.path, self.frame, self.draw_shake = ({}, [0, 0], ShakeComponent())

        self.free_enabled = False
        self.free_speed = 0.1
        self.free_input = {
            "up": "W",
            "down": "S",
            "left": "A",
            "right": "D",
            "in": "Q",
            "out": "E",
        }

        self.mouse_sensitivity = 0.05
        self.yaw = 0.0
        self.pitch = 0.0

    def update_view(self):
        self.view = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))

    def update_projection(self):
        self.projection = glm.perspective(glm.radians(50.0), self.aspect, 0.01, 50.0)

    def update(self, position=(0, 0, 0), target=(0, 0, 0), *args):
        position = self.next_position
        target = self.next_target

        target_vec = glm.vec3(*position)
        self.position += (target_vec - self.position) * self.smoothness + glm.vec3(
            self.draw_shake.update(0.016)
        )

        self.target = glm.vec3(*target)
        self.view = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))

    def get_focus_point(self, active_players=[], active_stages=[]):
        x_avg, y_avg = 0, 0
        for object in active_players:
            x_avg += object.position[0]
            y_avg += object.position[1]

        if not len(active_players):
            return

        x_avg /= len(active_players)
        y_avg /= len(active_players)

        position = [
            x_avg,
            y_avg + 3,
            8,
        ]

        limits = active_stages[0].dict["camera_focus_point_limit"]
        half_width = 6
        half_height = 4

        if position[0] - half_width < limits[0][0]:
            position[0] = limits[0][0] + half_width
        elif position[0] + half_width > limits[0][1]:
            position[0] = limits[0][1] - half_width

        if position[1] + half_height > limits[1][0]:
            position[1] = limits[1][0] - half_height
        elif position[1] - half_height < limits[1][1]:
            position[1] = limits[1][1] + half_height

        if self.path:
            path_frame = self.path["path"][self.frame[1]]
            obj = self.path["object"]
            scale = abs(16 / path_frame["position"]["vec"][2])
            zoom = (
                abs(self.next_position[2] / 16)
                if hasattr(self, "camera_next_position")
                else scale
            )

            cx, cy, cz = obj.position + rotate_vector(
                obj.rotation,
                (normalize_length(path_frame["position"]["vec"])),
            )
            cz = abs(cz)

            half_w = 6 * zoom
            half_h = 4 * zoom
            min_x = position[0] - 6 + half_w
            max_x = position[0] + 6 - half_w
            min_y = position[1] - 4 + half_h
            max_y = position[1] + 4 - half_h
            self.next_position = [
                clamp(cx, min_x, max_x),
                clamp(cy, min_y, max_y),
                cz,
            ]
            self.next_target = [
                self.next_position[0],
                self.next_position[1],
                self.next_position[2] - 100,
            ]
        else:
            self.next_position = position
            self.next_target = [
                self.next_position[0],
                self.next_position[1],
                self.next_position[2] - 100,
            ]

        if self.path:
            self.frame[0] += 1
            if self.frame[0] > self.path["path"][self.frame[1]]["dur"]:
                self.frame = [0, self.frame[1] + 1]
                if self.frame[1] >= len(self.path["path"]):
                    self.path, self.frame = {}, [0, 0]
