import numpy as np
import faiss
from scipy.spatial.distance import cosine

class MatchEngine:
    def __init__(self, embedding_dim=512):
        self.dim = embedding_dim
        # L2 Normalized inner product (Cosine Similarity) Index
        self.index = faiss.IndexFlatIP(self.dim)
        
    def calculate_similarity(self, target_emb, candidate_emb):
        # Cosine similarity (1 - Cosine Distance)
        return 1 - cosine(target_emb, candidate_emb)
        
    def add_to_db(self, embeddings):
        embeddings_np = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_np)
        self.index.add(embeddings_np)
        
    def search(self, target_emb, k=5):
        target_np = np.array([target_emb]).astype('float32')
        faiss.normalize_L2(target_np)
        distances, indices = self.index.search(target_np, k)
        return distances[0], indices[0]