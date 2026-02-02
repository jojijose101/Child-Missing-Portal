import cv2
import numpy as np
from keras_facenet import FaceNet

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = FaceNet()
    return _embedder

def get_embedding(face_rgb):
    face_rgb = cv2.resize(face_rgb, (160, 160))
    face_rgb = face_rgb.astype("float32")
    face_rgb = np.expand_dims(face_rgb, axis=0)

    embedder = get_embedder()
    return embedder.embeddings(face_rgb)[0]
