import cv2
import numpy as np
from insightface.app import FaceAnalysis


def patch_insightface_alignment():
    """Avoid skimage/scipy SimilarityTransform DLL errors on locked Windows PCs.

    InsightFace face_align uses skimage.transform internally. In this machine
    scipy DLL is blocked by Application Control policy, so target upload can
    crash before camera starts. OpenCV affine estimation is enough here.
    """
    try:
        import insightface.utils.face_align as face_align

        def estimate_norm_cv2(lmk, image_size=112, mode='arcface'):
            assert lmk.shape == (5, 2)
            if image_size % 112 == 0:
                ratio = float(image_size) / 112.0
                diff_x = 0
            else:
                ratio = float(image_size) / 128.0
                diff_x = 8.0 * ratio
            dst = face_align.arcface_dst * ratio
            dst[:, 0] += diff_x
            M, _ = cv2.estimateAffinePartial2D(lmk.astype(np.float32), dst.astype(np.float32), method=cv2.LMEDS)
            if M is None:
                M = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
            return M

        def transform_cv2(data, center, output_size, scale, rotation):
            M = cv2.getRotationMatrix2D((float(center[0]), float(center[1])), float(rotation), float(scale))
            M[0, 2] += output_size / 2.0 - center[0]
            M[1, 2] += output_size / 2.0 - center[1]
            cropped = cv2.warpAffine(data, M, (output_size, output_size), borderValue=0.0)
            return cropped, M

        face_align.estimate_norm = estimate_norm_cv2
        face_align.transform = transform_cv2
    except Exception as e:
        print(f"InsightFace alignment patch failed: {e}")

class FaceEngine:
    def __init__(self):
        print("Loading ArcFace (InsightFace) Model...")
        patch_insightface_alignment()
        # Detection + Recognition mattum load pannrom.
        # Landmark/gender-age modules scipy/skimage DLL issue kudukkalam; camera start block aagakoodathu.
        self.app = FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
    def get_embedding(self, image):
        """ஒரு புகைப்படத்தில் உள்ள முகத்தை AI எண்களாக (Embeddings) மாற்றும்"""
        if image is None:
            return None
        try:
            faces = self.app.get(image)
        except Exception as e:
            print(f"Face embedding error: {e}")
            return None
        if len(faces) == 0:
            return None
        
        # படத்தில் பல முகங்கள் இருந்தாலும், முதல் முகத்தை மட்டும் எடுத்துக்கொள்ளும்
        return faces[0].embedding
        
    def compare_faces(self, embedding1, embedding2):
        """இரண்டு முகங்களுக்கு இடையிலான ஒற்றுமையை (Similarity) 0-100% ஆகக் கணக்கிடும்"""
        if embedding1 is None or embedding2 is None:
            return 0.0
            
        # Cosine Similarity Formula
        sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        match_percentage = max(0, sim * 100)
        
        return round(match_percentage, 2)
