import cv2
from mtcnn import MTCNN

_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = MTCNN()
    return _detector

def detect_face(image_path, margin=20):
    """
    Returns cropped face in RGB format (numpy array) or None
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return None

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    detector = get_detector()
    faces = detector.detect_faces(img_rgb)

    if not faces:
        return None

    # ✅ pick the largest face (best for group images)
    faces = sorted(faces, key=lambda f: f["box"][2] * f["box"][3], reverse=True)
    x, y, w, h = faces[0]["box"]

    H, W = img_rgb.shape[:2]
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(W, x + w + margin)
    y2 = min(H, y + h + margin)

    face_rgb = img_rgb[y1:y2, x1:x2]
    if face_rgb.size == 0:
        return None

    return face_rgb
