from os.path import exists, splitext

import pygame
import pygame.image as image
from OpenGL.GL import *
from glm import vec2
from pygame import BLEND_RGBA_MULT


def loadTexture(imagePath, alpha=0, imageLoad=None):
    oldTextureSurface = imageLoad or image.load(imagePath).convert_alpha()

    width = oldTextureSurface.get_width()
    height = oldTextureSurface.get_height()

    textureSurface = oldTextureSurface.copy()
    if alpha != 0:
        textureSurface.fill((255, 255, 255, alpha), None, special_flags=BLEND_RGBA_MULT)
    # textureSurface.fill((0, 255, 100))

    textureData = image.tostring(textureSurface, "RGBA", True)

    # glEnable(GL_TEXTURE_2D)
    textureId = glGenTextures(1)
    # https://learnopengl.com/Advanced-OpenGL/Anti-Aliasing

    glBindTexture(GL_TEXTURE_2D, textureId)

    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return textureId


def loadAnimation(imageFirstPath, returnImage=False):  # Example: menu-back@2x.png
    pathSplit = splitext(imageFirstPath)
    imageFormat = pathSplit[0] + "{||}" + pathSplit[1]

    if "@2x" in imageFormat:
        imageFormat = imageFormat.replace("@2x{||}", "{||}@2x", 1)

    imageLoads = []  # Ignore First
    animationTextures = []

    i = 0
    while True:
        newImagePath = imageFormat.replace(r"{||}", f"-{i}", 1)

        if not exists(newImagePath):
            break

        imageLoads.append(newImagePath)

        i += 1

    for imageLoadPath in imageLoads:
        animationTextures.append(loadTexture(imageLoadPath))

    if not returnImage:
        return animationTextures
    else:
        return animationTextures, imageLoads


def GetImageScaleSize(image, scale, displayV, heightWidthScale=True, tuple=False):
    if heightWidthScale:
        lengthP = scale * displayV.y

        sizeRatio = image.get_width() / image.get_height()
        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.x

        if tuple:
            return oLength, scale
        else:
            return vec2(oLength, scale)

    else:
        lengthP = scale * displayV.x
        sizeRatio = image.get_height() / image.get_width()

        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.y

        if tuple:
            return scale, oLength
        else:
            return vec2(scale, oLength)
