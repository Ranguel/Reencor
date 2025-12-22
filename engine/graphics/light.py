import glm


class Light:
    def __init__(self, size, smoothness=0.1):
        self.type = "light"
        self.position = glm.vec3(0, 14, 14)
        self.target = glm.vec3(0, 0, 0)

        self.view = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))
        self.projection = glm.ortho(-size, size, -size, size, 0.01, 60.0)
        self.vp = self.projection * self.view

        self.smoothness = smoothness

        self.next_position = [0, 0, 0]
        self.next_target = [0, 0, 0]

    def update(self, position=(0, 0, 0), target=(0, 0, 0), *args):
        position = self.next_position
        target = self.next_target

        target_vec = glm.vec3(*position)
        self.position += (target_vec - self.position) * self.smoothness

        self.target = glm.vec3(*target)
        self.view = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))
