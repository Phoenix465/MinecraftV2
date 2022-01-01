from glm import vec3, vec4


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


class DefaultBlockFaceFill:
    def __init__(self, centre: vec3 = vec3()):
        self.vertices = [
            vec4(centre, 0) + relVec for relVec in [
                vec4( 0.5, 0,  0.5, 0),  # 0
                vec4(-0.5, 0,  0.5, 0),  # 1
                vec4(-0.5, 0, -0.5, 0),  # 2
                vec4( 0.5, 0, -0.5, 0),  # 3

                vec4( 0.5, 1,  0.5, 1),  # 4
                vec4(-0.5, 1,  0.5, 1),  # 5
                vec4(-0.5, 1, -0.5, 1),  # 6
                vec4( 0.5, 1, -0.5, 1),  # 7

                vec4( 0.5, 0,  0.5, 2),  # 8
                vec4( 0.5, 0, -0.5, 2),  # 9
                vec4( 0.5, 1, -0.5, 2),  # 10
                vec4( 0.5, 1,  0.5, 2),  # 11

                vec4(-0.5, 0,  0.5, 3),  # 12
                vec4(-0.5, 0, -0.5, 3),  # 13
                vec4(-0.5, 1, -0.5, 3),  # 14
                vec4(-0.5, 1,  0.5, 3),  # 15

                vec4( 0.5, 0, 0.5, 4),  # 16
                vec4(-0.5, 0, 0.5, 4),  # 17
                vec4(-0.5, 1, 0.5, 4),  # 18
                vec4( 0.5, 1, 0.5, 4),  # 19

                vec4( 0.5, 0, -0.5, 5),  # 20
                vec4(-0.5, 0, -0.5, 5),  # 21
                vec4(-0.5, 1, -0.5, 5),  # 22
                vec4( 0.5, 1, -0.5, 5),  # 23
        ]]

        self.indices = [
            (0, 1, 2), (0, 3, 2),  # Bottom
            (4, 5, 6), (4, 7, 6),  # Top

            (8, 9, 10), (8, 11, 10),  # Right
            (12, 13, 14), (12, 15, 14),  # Left

            (16, 17, 18), (16, 19, 18),  # Front
            (20, 21, 22), (20, 23, 22),  # Back
        ]
