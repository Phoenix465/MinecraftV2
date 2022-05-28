from PIL import Image
import numpy as np


noise = r"top.png"
colour = np.array([112/255, 176/255, 70/255, 1], dtype=np.float32)

image = Image.open(noise)
imageA = np.asarray(image, dtype=np.float32)
#imageA = (1 - (1-imageA/255)*(1-colour)) * 255
imageA = imageA/imageA.max(axis=0) * colour * 255
newImage = np.array(imageA, dtype=np.uint8)
img = Image.fromarray(newImage, 'RGBA')
img.save(r"top2.png")
