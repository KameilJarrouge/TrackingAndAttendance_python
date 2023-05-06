from RecognitionFunction import recognize

import skimage
import numpy as np

image = skimage.io.imread(
    "http://localhost:8000/storage/profiles/1-image1.png")
image2 = np.delete(image, 3, 2)
print(image2.shape)
print(image2)
print(recognize(image2,
      image2))
