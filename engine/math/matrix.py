import glm


def get_model_matrix(position=(0, 0), size=(0, 0), rotation=(0, 0, 0)):
    rotation_matrix = glm.mat4(1.0)
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[0]), glm.vec3(1, 0, 0)
    )
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[1]), glm.vec3(0, 1, 0)
    )
    rotation_matrix = glm.rotate(
        rotation_matrix, glm.radians(rotation[2]), glm.vec3(0, 0, 1)
    )

    model = glm.scale(
        glm.translate(glm.mat4(1.0), glm.vec3(position[0], position[1], position[2]))
        * rotation_matrix,
        glm.vec3(
            size[0],
            size[1],
            1.0,
        ),
    )

    return model
