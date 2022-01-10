import sys
from os import path


class PathHolder:
    def __init__(self):
        self.shaderPath = path.join(".", "shaders")

        self.vertexPath = path.join(self.shaderPath, "MainVertex.shader")
        self.fragmentPath = path.join(self.shaderPath, "MainFragment.shader")
        self.defaultShaderPaths = (self.vertexPath, self.fragmentPath)

        self.UIPlainVertexPath = path.join(self.shaderPath, "UIPlainVertex.shader")
        self.UIPlainFragmentPath = path.join(self.shaderPath, "UIPlainFragment.shader")
        self.UIPlainShaderPaths = (self.UIPlainVertexPath, self.UIPlainFragmentPath)
