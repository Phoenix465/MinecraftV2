import sys
from os import path


class PathHolder:
    def __init__(self):
        self.shaderPath = path.join(".", "shaders")
        self.resources = path.abspath(path.join(".", "resources"))

        self.vertexPath = path.join(self.shaderPath, "MainVertex.shader")
        self.fragmentPath = path.join(self.shaderPath, "MainFragment.shader")
        self.defaultShaderPaths = (self.vertexPath, self.fragmentPath)

        self.UIPlainVertexPath = path.join(self.shaderPath, "UIPlainVertex.shader")
        self.UIPlainFragmentPath = path.join(self.shaderPath, "UIPlainFragment.shader")
        self.UIPlainShaderPaths = (self.UIPlainVertexPath, self.UIPlainFragmentPath)
        
        self.UIVertexPath = path.join(self.shaderPath, "UIVertex.shader")
        self.UIFragmentPath = path.join(self.shaderPath, "UIFragment.shader")
        self.UIShaderPaths = (self.UIVertexPath, self.UIFragmentPath)

        self.imagesPath = path.join(self.resources, "images")
        self.scorePath = path.join(self.imagesPath, "score")
        self.scoreBasePath = path.join(self.scorePath, "score@2x.png")

        self.blockPath = path.join(self.imagesPath, "block")
        self.blockAtlasPath = path.join(self.blockPath, "atlas.png")