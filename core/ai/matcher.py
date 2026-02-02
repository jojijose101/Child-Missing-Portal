import pickle
import numpy as np

def find_best_match(query_embedding, children_qs, threshold=1.0):
    best_child = None
    best_dist = 999999.0

    for child in children_qs:
        if not child.embedding:
            continue
        try:
            db_emb = pickle.loads(child.embedding)
        except Exception:
            continue

        dist = np.linalg.norm(db_emb - query_embedding)
        print(f"Comparing with {child.name}, Distance: {dist:.4f}")

        if dist < best_dist:
            best_dist = dist
            print(f"New best match: {child.name} with distance {best_dist:.4f}")
            best_child = child

    if best_child and best_dist < threshold:
        return best_child, best_dist
    

    return None, best_dist
