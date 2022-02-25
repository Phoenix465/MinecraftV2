from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, glGetShaderiv, GL_COMPILE_STATUS, GL_INFO_LOG_LENGTH, glGetShaderInfoLog


def loadShader(shader_file):
    with open(shader_file) as f:
        shader_source = f.read()
    f.close()
    return str.encode(shader_source)


def compileShaders(vs, fs):
    vert_shader = loadShader(vs)
    frag_shader = loadShader(fs)

    vertexShader = compileShader(vert_shader, GL_VERTEX_SHADER)
    fragShader = compileShader(frag_shader, GL_FRAGMENT_SHADER)

    for tShader in [vertexShader, fragShader]:
        isCompiled = glGetShaderiv(tShader, GL_COMPILE_STATUS)
        if not isCompiled:
            maxLength = glGetShaderiv(tShader, GL_INFO_LOG_LENGTH)
            log = glGetShaderInfoLog(tShader, maxLength)
            raise Exception(log)

    shader = compileProgram(vertexShader, fragShader)

    return shader
