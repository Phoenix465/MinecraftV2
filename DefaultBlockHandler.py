from glm import vec3


class DefaultBlock:
    def __init__(self, centre: vec3 = vec3()):
        self.vertices = [
            centre + relVec for relVec in [
                vec3( 0.5, 0,  0.5),
                vec3(-0.5, 0,  0.5),
                vec3(-0.5, 0, -0.5),
                vec3( 0.5, 0, -0.5),
                vec3( 0.5, 1,  0.5),
                vec3(-0.5, 1,  0.5),
                vec3(-0.5, 1, -0.5),
                vec3( 0.5, 1, -0.5),
        ]]

        self.indices = [
            (0, 1, 2),  # Bottom
            (0, 2, 3),  # Bottom

            (4, 5, 6),   # Top
            (4, 6, 7),   # Top

            (0, 4, 7),   # Right
            (0, 7, 3),   # Right

            (1, 5, 6),   # Left
            (1, 6, 2),   # Left

            (2, 6, 7),   # Front
            (2, 7, 3),   # Front

            (1, 5, 4),   # Back
            (1, 4, 0),   # Back
        ]

        self.normals = [
            vec3(0, -1, 0),
            vec3(0,  1, 0),
            vec3( 1, 0, 0),
            vec3(-1, 0, 0),
            vec3(0, 0, -1),
            vec3(0, 0,  1),
        ]
