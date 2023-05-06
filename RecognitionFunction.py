from deepface import DeepFace


def recognize(webcamImage, sourceImage):
    verification = DeepFace.verify(webcamImage,
                                   sourceImage, enforce_detection=False, model_name='Facenet512', prog_bar=False)
    return verification['verified']
