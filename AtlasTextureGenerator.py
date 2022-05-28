import numpy as np
from PIL import Image

import Enumerations
import os.path as path
import GamePathHandler


def generateBlockAtlas():
    pathHandler = GamePathHandler.PathHolder()
    blockPath = pathHandler.blockPath
    fileNames = ["all", "side", "top", "bottom", "left", "right", "front", "back"]

    # Get Max Value
    maxBlockType = 0
    for name in Enumerations.BlockType:
        maxBlockType = max(maxBlockType, name.value)

    blockImages = []
    maxSize = 0

    for blockI in range(0, maxBlockType+1):
        blockFacePaths = {
            "bottom": None,
            "top": None,
            "right": None,
            "left": None,
            "back": None,
            "front": None,
        }

        try:
            name = Enumerations.BlockType(blockI).name
        except ValueError:
            blockImages.append(blockFacePaths)
            continue

        blockName = str(name).split(".")[-1]
        newPath = path.join(blockPath, blockName)

        if path.isdir(newPath):
            allPath = path.join(newPath, f"{fileNames[0]}.png")

            if path.isfile(allPath):
                blockFacePaths["top"] = allPath
                blockFacePaths["bottom"] = allPath
                blockFacePaths["left"] = allPath
                blockFacePaths["right"] = allPath
                blockFacePaths["front"] = allPath
                blockFacePaths["back"] = allPath

                image = Image.open(allPath)
                imageA = np.asarray(image, dtype=np.float32)

                if imageA.shape[0] != imageA.shape[1]:
                    raise Exception(f"Block Texture {blockName}:all is not Square")

                maxSize = max(maxSize, imageA.shape[0])

            else:
                for faceT in fileNames[1:]:
                    facePath = path.join(newPath, f"{faceT}.png")

                    if path.isfile(facePath):
                        if faceT == "side":
                            blockFacePaths["front"] = facePath
                            blockFacePaths["back"] = facePath
                            blockFacePaths["left"] = facePath
                            blockFacePaths["right"] = facePath
                        else:
                            blockFacePaths[faceT] = facePath

                        image = Image.open(facePath)
                        imageA = np.asarray(image, dtype=np.float32)

                        if imageA.shape[0] != imageA.shape[1]:
                            raise Exception(f"Block Texture {blockName}:{faceT} is not Square")

                        maxSize = max(maxSize, imageA.shape[0])

        blockImages.append(blockFacePaths)

    # Height, Width, RGBA
    blockAtlas = np.zeros(((maxBlockType+1) * maxSize, 6 * maxSize, 4))
    for rowI, blockImageData in enumerate(blockImages):
        for columnI, imagePath in enumerate(blockImageData.values()):
            if imagePath is not None:
                image = Image.open(imagePath)
                imageA = np.asarray(image, dtype=np.uint8)

                xOffset = rowI * maxSize
                yOffset = columnI * maxSize

                blockAtlas[xOffset:xOffset+maxSize, yOffset:yOffset+maxSize] = imageA
    # blockAtlas[:, :, 3] = 255

    blockAtlas = np.array(blockAtlas, dtype=np.uint8)
    img = Image.fromarray(blockAtlas, 'RGBA')
    img.save(pathHandler.blockAtlasPath)


if __name__ == "__main__":
    generateBlockAtlas()
