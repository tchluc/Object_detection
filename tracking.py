from sklearn.metrics.pairwise import cosine_similarity
import config

def find_best_match(embedding, tracks_snapshot):
    """
    Finds the best matching Global ID for a given embedding.

    Args:
        embedding (np.array): Visual feature vector of the current object.
        tracks_snapshot (dict): Read-only copy of global tracks {gid: data}.

    Returns:
        tuple: (best_match_id, best_similarity_score) OR (None, -1.0)
    """
    best_match_id = None
    best_sim = -1.0
    
    for g_id, data in tracks_snapshot.items():
        # cosine_similarity expects 2D arrays (1, n_features)
        sim = cosine_similarity(embedding.reshape(1, -1), data['embedding'].reshape(1, -1))[0][0]
        if sim > best_sim:
            best_sim = sim
            best_match_id = g_id
            
    return best_match_id, best_sim

def update_global_track(shared_global_tracks, gid, embedding, pos, video_name, lock):
    """
    Updates the shared global track data safely.
    """
    with lock:
        d = shared_global_tracks[gid]
        d['embedding'] = embedding
        d['last_pos'] = pos
        d['last_video'] = video_name
        shared_global_tracks[gid] = d

def create_new_track(shared_global_tracks, global_id_counter, embedding, pos, video_name, lock):
    """
    Creates a new global track safely.
    """
    with lock:
        new_gid = global_id_counter.value
        global_id_counter.value += 1
        shared_global_tracks[new_gid] = {
            'embedding': embedding, 
            'last_pos': pos, 
            'last_video': video_name
        }
        return new_gid
